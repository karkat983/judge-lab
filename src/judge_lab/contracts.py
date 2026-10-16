"""Frozen v1 boundary models. Validation failures expose codes, never submitted values."""

from datetime import datetime, timedelta
from typing import Annotated, Any, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ModelWrapValidatorHandler,
    StringConstraints,
    ValidationError,
    field_validator,
    model_validator,
)

Identifier = Annotated[str, StringConstraints(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,127}$")]
Digest = Annotated[str, StringConstraints(pattern=r"^sha256:[0-9a-f]{64}$")]
Text = Annotated[str, StringConstraints(min_length=1, max_length=32768)]
ReferenceLabel = Literal["ACCEPT", "REJECT"]
Prediction = Literal["ACCEPT", "REJECT", "ABSTAIN"]
Outcome = Literal["ACCEPT", "REJECT", "ABSTAIN", "ERROR"]
ErrorKind = Literal["INVALID_INPUT", "PARSE_ERROR", "TIMEOUT", "PROVIDER_ERROR", "BUDGET_EXCEEDED"]
Split = Literal["development", "calibration_200", "heldout_test"]
Nonnegative = Annotated[float, Field(ge=0, allow_inf_nan=False)]
Count = Annotated[int, Field(ge=0, le=1_000_000_000)]


class ContractError(Exception):
    """Sanitized boundary failure; no original payload, path or provider error attached as text."""

    def __init__(self, code: Literal["INVALID_INPUT", "PARSE_ERROR", "INTEGRITY_ERROR", "INPUT_TOO_LARGE"]):
        self.code = code
        super().__init__(code)


class FrozenModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid", strict=True, frozen=True, allow_inf_nan=False,
        hide_input_in_errors=True, revalidate_instances="always",
    )

    @model_validator(mode="wrap")
    @classmethod
    def private_validation(cls, value: Any, handler: ModelWrapValidatorHandler[Self]) -> Self:
        try:
            return handler(value)
        except ValidationError:
            raise ContractError("INVALID_INPUT") from None

    @field_validator("*", mode="before")
    @classmethod
    def freeze_arrays(cls, value: Any) -> Any:
        # JSON arrays become tuples; element values still undergo strict validation.
        return tuple(value) if isinstance(value, list) else value

    @field_validator("*", mode="after")
    @classmethod
    def valid_text(cls, value: Any) -> Any:
        if isinstance(value, str):
            try:
                value.encode("utf-8", errors="strict")
            except UnicodeError:
                raise ContractError("INVALID_INPUT") from None
            if not value.strip() or "\x00" in value:
                raise ContractError("INVALID_INPUT")
        return value

    def __repr__(self) -> str:
        return f"{type(self).__name__}(<private>)"

    def __str__(self) -> str:
        return self.__repr__()


class Versioned(FrozenModel):
    schema_version: Literal["1.0"]


class Evidence(FrozenModel):
    id: Identifier
    type: Literal["log", "alert", "note"]
    text: Text


class PolicyConstraints(FrozenModel):
    allowed_actions: Annotated[tuple[Identifier, ...], Field(max_length=64)]
    prohibited_actions: Annotated[tuple[Identifier, ...], Field(max_length=64)]

    @model_validator(mode="after")
    def no_conflicts(self) -> Self:
        allowed, prohibited = set(self.allowed_actions), set(self.prohibited_actions)
        if (allowed & prohibited or len(allowed) != len(self.allowed_actions)
                or len(prohibited) != len(self.prohibited_actions)):
            raise ContractError("INVALID_INPUT")
        return self


class JudgeInput(Versioned):
    """Rubric-authorized content only; association with case IDs stays outside the model payload."""

    rubric_revision: Identifier
    report_text: Text
    authoritative_evidence: Annotated[tuple[Evidence, ...], Field(min_length=1, max_length=64)]
    policy_constraints: PolicyConstraints


class Case(JudgeInput):
    case_id: Identifier
    case_family_id: Identifier
    split: Split
    reference_label: ReferenceLabel
    reference_reason_codes: Annotated[tuple[Identifier, ...], Field(max_length=64)]
    reference_source: Identifier
    adjudication_id: Identifier
    reference_frozen: Literal[True]

    @field_validator("reference_frozen", mode="before")
    @classmethod
    def actually_frozen(cls, value: Any) -> bool:
        if value is not True:
            raise ContractError("INVALID_INPUT")
        return True

    @model_validator(mode="after")
    def consistent_case(self) -> Self:
        ids = [item.id for item in self.authoritative_evidence]
        if len(set(ids)) != len(ids):
            raise ContractError("INVALID_INPUT")
        if self.reference_label == "REJECT" and not self.reference_reason_codes:
            raise ContractError("INVALID_INPUT")
        return self

    def judge_input(self) -> JudgeInput:
        # Never dump Case wholesale or inherit new reference fields into a prompt.
        return JudgeInput(
            schema_version=self.schema_version, rubric_revision=self.rubric_revision,
            report_text=self.report_text, authoritative_evidence=self.authoritative_evidence,
            policy_constraints=self.policy_constraints,
        )


class Timestamped(Versioned):
    created_at_utc: datetime

    @field_validator("created_at_utc", mode="before")
    @classmethod
    def utc_only(cls, value: Any) -> datetime:
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                raise ContractError("INVALID_INPUT") from None
        if not isinstance(value, datetime) or value.utcoffset() != timedelta(0):
            raise ContractError("INVALID_INPUT")
        return value


class DatasetRevision(Timestamped):
    dataset_id: Identifier
    dataset_revision: Identifier
    label_protocol_revision: Identifier
    source: Text
    license_or_permission: Text
    reference_provenance: Text
    evidence_status: Literal["SYNTHETIC", "HUMAN_ADJUDICATED"]
    split_algorithm: Text
    split_seed: Count
    sha256: Digest


class JudgeSettings(FrozenModel):
    temperature: Annotated[float, Field(ge=0, le=2)]
    max_output_tokens: Annotated[int, Field(gt=0, le=32768)]


class ExecutionLimits(FrozenModel):
    max_calls: Annotated[int, Field(gt=0, le=1_000_000)]
    timeout_seconds: Annotated[float, Field(gt=0, le=3600)]
    max_cost_usd: Nonnegative


class JudgeSpec(Versioned):
    judge_id: Identifier
    adapter: Literal["deterministic_mock", "imported"]
    model_ref: Identifier
    rubric_revision: Identifier
    rubric_text: Text
    parser: Literal["strict_label"]
    settings: JudgeSettings
    limits: ExecutionLimits


class JudgeResult(Versioned):
    case_id: Identifier
    case_digest: Digest
    run_id: Digest
    judge_spec_digest: Digest
    verdict: Outcome
    error_kind: ErrorKind | None
    raw_output_ref: None = None
    latency_ms: Nonnegative
    input_tokens: Count
    output_tokens: Count
    estimated_cost_usd: Nonnegative | None

    @model_validator(mode="after")
    def error_is_explicit(self) -> Self:
        if (self.verdict == "ERROR") != (self.error_kind is not None):
            raise ContractError("INVALID_INPUT")
        return self


class RunEnvironment(FrozenModel):
    python: Identifier
    platform: Identifier
    package_version: Identifier


class RunManifest(Timestamped):
    run_id: Digest
    dataset_digest: Digest
    dataset_manifest_digest: Digest
    label_protocol_revision: Identifier
    rubric_digest: Digest
    judge_spec_digest: Digest
    split_digest: Digest
    adapter_version: Identifier
    run_seed: Count
    environment: RunEnvironment
    limits: ExecutionLimits
