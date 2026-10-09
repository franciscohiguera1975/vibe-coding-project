"""ConsoleEmailAdapter (equivalente a MockAIAdapter): implementacion de EmailSender sin
red, usada por defecto en desarrollo/pruebas (EMAIL_PROVIDER=console). Imprime el enlace
de restablecimiento a stdout en vez de enviarlo, suficiente para ejercitar el flujo
completo sin depender de credenciales SMTP. Se usa print() y no el modulo logging
(que este proyecto no configura en ningun otro punto) para que el enlace sea visible
de forma confiable en la consola del backend, sin depender del nivel de log efectivo."""


class ConsoleEmailAdapter:
    def send_password_reset_email(self, *, to_email: str, full_name: str, reset_url: str) -> None:
        print(
            f"[email:console] Restablecimiento de contraseña para {full_name} <{to_email}>: "
            f"{reset_url}"
        )
