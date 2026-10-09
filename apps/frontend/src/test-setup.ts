import '@testing-library/jest-dom/vitest';
import i18n from '@/infrastructure/i18n';

// Los componentes migrados a react-i18next usan useTranslation() con el idioma
// detectado del navegador. jsdom reporta "en-US" por defecto, lo que haría que
// las pruebas (escritas contra el texto en español, la fuente de verdad)
// fallen. Fijamos el idioma a español para que las aserciones existentes sigan
// siendo válidas sin tener que duplicarlas por idioma.
void i18n.changeLanguage('es');
