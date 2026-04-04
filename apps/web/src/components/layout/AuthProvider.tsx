"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import {
  AuthUser,
  getCurrentUser,
  isAuthenticated,
  loginUser as loginApi,
  logout as logoutApi,
  registerUser as registerApi,
} from "@/lib/auth";
import { useRouter } from "next/navigation";

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (
    name: string,
    email: string,
    password: string,
  ) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated()) {
      getCurrentUser()
        .then(setUser)
        .catch(() => {
          logoutApi();
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      await loginApi(email, password);
      const currentUser = await getCurrentUser();
      setUser(currentUser);
      router.push("/chat");
    },
    [router],
  );

  const register = useCallback(
    async (name: string, email: string, password: string) => {
      await registerApi(name, email, password);
      await loginApi(email, password);
      const currentUser = await getCurrentUser();
      setUser(currentUser);
      router.push("/chat");
    },
    [router],
  );

  const logout = useCallback(() => {
    logoutApi();
    setUser(null);
    router.push("/login");
  }, [router]);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    return {
      user: null,
      loading: false,
      login: async () => {},
      register: async () => {},
      logout: () => {},
    };
  }
  return context;
}
