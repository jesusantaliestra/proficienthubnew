/**
 * ProficientHub - Authentication Utilities
 *
 * Security best practices for token management:
 *
 * CURRENT IMPLEMENTATION (localStorage):
 * - Suitable for development and low-security scenarios
 * - Vulnerable to XSS attacks
 *
 * RECOMMENDED FOR PRODUCTION:
 * - Use httpOnly cookies set by the backend
 * - Implement CSRF protection
 * - Use short-lived access tokens with refresh tokens
 *
 * To migrate to httpOnly cookies:
 * 1. Backend sets token in httpOnly cookie on login
 * 2. Frontend sends credentials: 'include' with fetch
 * 3. Remove localStorage token storage
 */

const TOKEN_KEY = 'token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const TOKEN_EXPIRY_KEY = 'token_expiry';

/**
 * Authentication service for managing tokens
 */
class AuthService {
  /**
   * Store authentication token
   * @param {string} token - JWT access token
   * @param {number} expiresIn - Token expiration in seconds
   */
  setToken(token, expiresIn = 3600) {
    try {
      const expiry = Date.now() + expiresIn * 1000;
      sessionStorage.setItem(TOKEN_KEY, token);
      sessionStorage.setItem(TOKEN_EXPIRY_KEY, expiry.toString());
    } catch (error) {
      console.error('Failed to store token:', error);
    }
  }

  /**
   * Get current authentication token
   * @returns {string|null} Token if valid, null otherwise
   */
  getToken() {
    try {
      const token = sessionStorage.getItem(TOKEN_KEY);
      const expiry = sessionStorage.getItem(TOKEN_EXPIRY_KEY);

      if (!token) return null;

      // Check if token has expired
      if (expiry && Date.now() > parseInt(expiry, 10)) {
        this.clearAuth();
        return null;
      }

      return token;
    } catch (error) {
      console.error('Failed to retrieve token:', error);
      return null;
    }
  }

  /**
   * Store refresh token (if using refresh token flow)
   * @param {string} refreshToken - Refresh token
   */
  setRefreshToken(refreshToken) {
    try {
      // In production, refresh tokens should be in httpOnly cookies
      sessionStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    } catch (error) {
      console.error('Failed to store refresh token:', error);
    }
  }

  /**
   * Get refresh token
   * @returns {string|null}
   */
  getRefreshToken() {
    try {
      return sessionStorage.getItem(REFRESH_TOKEN_KEY);
    } catch (error) {
      return null;
    }
  }

  /**
   * Clear all authentication data
   */
  clearAuth() {
    try {
      sessionStorage.removeItem(TOKEN_KEY);
      sessionStorage.removeItem(REFRESH_TOKEN_KEY);
      sessionStorage.removeItem(TOKEN_EXPIRY_KEY);
      // Also clear from localStorage for migration
      localStorage.removeItem('token');
    } catch (error) {
      console.error('Failed to clear auth:', error);
    }
  }

  /**
   * Check if user is authenticated
   * @returns {boolean}
   */
  isAuthenticated() {
    return !!this.getToken();
  }

  /**
   * Get authorization headers for API requests
   * @returns {Object} Headers object with Authorization
   */
  getAuthHeaders() {
    const token = this.getToken();
    if (!token) {
      return {};
    }
    return {
      Authorization: `Bearer ${token}`,
    };
  }
}

// Singleton instance
export const authService = new AuthService();

/**
 * Fetch wrapper with automatic authentication
 * Handles token refresh and redirects to login on 401
 *
 * @param {string} url - API endpoint
 * @param {Object} options - Fetch options
 * @returns {Promise<Response>}
 */
export async function authFetch(url, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...authService.getAuthHeaders(),
    ...options.headers,
  };

  const response = await fetch(url, {
    ...options,
    headers,
    // For httpOnly cookies in production:
    // credentials: 'include',
  });

  // Handle authentication errors
  if (response.status === 401) {
    authService.clearAuth();
    // Redirect to login or emit event
    window.dispatchEvent(new CustomEvent('auth:logout'));
    throw new AuthenticationError('Session expired. Please log in again.');
  }

  return response;
}

/**
 * Custom error for authentication failures
 */
export class AuthenticationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'AuthenticationError';
  }
}

/**
 * Parse and validate JWT token (without verification)
 * Note: Always verify tokens server-side
 *
 * @param {string} token - JWT token
 * @returns {Object|null} Decoded payload or null
 */
export function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    return null;
  }
}

/**
 * Check if token is about to expire (within threshold)
 *
 * @param {number} thresholdSeconds - Seconds before expiry to consider "expiring"
 * @returns {boolean}
 */
export function isTokenExpiringSoon(thresholdSeconds = 300) {
  const expiry = sessionStorage.getItem(TOKEN_EXPIRY_KEY);
  if (!expiry) return true;

  const timeUntilExpiry = parseInt(expiry, 10) - Date.now();
  return timeUntilExpiry < thresholdSeconds * 1000;
}

// Migration helper: move token from localStorage to sessionStorage
(function migrateToken() {
  const oldToken = localStorage.getItem('token');
  if (oldToken && !sessionStorage.getItem(TOKEN_KEY)) {
    sessionStorage.setItem(TOKEN_KEY, oldToken);
    localStorage.removeItem('token');
  }
})();

export default authService;
