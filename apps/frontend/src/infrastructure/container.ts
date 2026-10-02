/** Raiz de composicion: unico lugar donde la capa de presentacion puede tocar un
 * detalle de infraestructura (la instancia concreta de ApiClient). Todo lo demas
 * depende solo de los servicios de application/, que a su vez dependen solo del
 * puerto HttpClient. */
import { AuthService } from '@/application/services/auth-service';
import { CatalogService } from '@/application/services/catalog-service';
import { PracticeService } from '@/application/services/practice-service';
import { RoleService } from '@/application/services/role-service';
import { SystemService } from '@/application/services/system-service';
import { UserService } from '@/application/services/user-service';
import { apiClient } from '@/infrastructure/http/api-client';
import { tokenStorage } from '@/infrastructure/auth/local-token-storage';

export const authService = new AuthService(apiClient);
export const practiceService = new PracticeService(apiClient);
export const userService = new UserService(apiClient);
export const roleService = new RoleService(apiClient);
export const catalogService = new CatalogService(apiClient);
export const systemService = new SystemService(apiClient);
export { tokenStorage };
