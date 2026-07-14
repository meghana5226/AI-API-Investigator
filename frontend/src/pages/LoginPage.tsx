import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { SearchCode, Loader2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { isAxiosError } from "axios";

interface LoginForm {
  email: string;
  password: string;
}

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>();

  const onSubmit = async (data: LoginForm) => {
    setIsSubmitting(true);
    try {
      await login(data.email, data.password);
      toast.success("Welcome back!");
      navigate("/dashboard");
    } catch (err) {
      const message = isAxiosError(err) ? err.response?.data?.detail : "Login failed";
      toast.error(message || "Login failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink-900 px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-accent/20 text-accent">
            <SearchCode className="h-6 w-6" />
          </div>
          <h1 className="mt-4 text-xl font-bold text-slate-100">Sign in to your account</h1>
          <p className="mt-1 text-sm text-slate-500">Investigate APIs with AI-powered analysis</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="card space-y-4 p-6">
          <div>
            <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-slate-300">Email</label>
            <input
              id="email"
              type="email"
              className="input-field"
              placeholder="you@example.com"
              {...register("email", { required: "Email is required" })}
            />
            {errors.email && <p className="mt-1 text-xs text-red-400">{errors.email.message}</p>}
          </div>
          <div>
            <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-slate-300">Password</label>
            <input
              id="password"
              type="password"
              className="input-field"
              placeholder="••••••••"
              {...register("password", { required: "Password is required" })}
            />
            {errors.password && <p className="mt-1 text-xs text-red-400">{errors.password.message}</p>}
          </div>
          <button type="submit" disabled={isSubmitting} className="btn-primary w-full">
            {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
            Sign in
          </button>
          <p className="rounded-lg bg-ink-900 px-3 py-2 text-center text-xs text-slate-500">
            Demo login: <span className="mono text-slate-400">demo@apiinvestigator.dev</span> /{" "}
            <span className="mono text-slate-400">DemoPass123!</span>
          </p>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500">
          Don't have an account?{" "}
          <Link to="/register" className="font-medium text-accent-light hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}
