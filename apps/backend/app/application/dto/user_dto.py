from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CreateUserInput:
    email: str
    full_name: str
    password: str
    role_names: list[str] = field(default_factory=list)
