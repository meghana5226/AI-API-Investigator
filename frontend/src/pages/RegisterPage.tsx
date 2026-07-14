import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { SearchCode, Loader2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { isAxiosError } from "axios";

interface RegisterForm {
  full_name: string;
  email: string;
  password: string;
  confirm_password: string;
}

export function RegisterPage() {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterForm>();

  const onSubmit = async (data: RegisterForm) => {
    setIsSubmitting(true);
    try {
      await registerUser(data.email, data.full_name, data.password);
      toast.success("Account created!");
      navigate("/dashboard");
    } catch (err) {
      const message = isAxiosError(err) ? err.response?.data?.detail : "Registration failed";
      toast.error(message || "Registration failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink-900 px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-accent/20 text-accent">
            <SearchCode className="h-6 w-6" />
          </div>
          <h1 className="mt-4 text-xl font-bold text-slate-100">Create your account</h1>
          <p className="mt-1 text-sm text-slate-500">Start investigating APIs in seconds</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="card space-y-4 p-6">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-300">Full name</label>
            <input
              className="input-field"
              placeholder="Jane Doe"
              {...register("full_name", { required: "Name is required", minLength: { value: 2, message: "Too short" } })}
            />
            {errors.full_name && <p className="mt-1 text-xs text-red-400">{errors.full_name.message}</p>}
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-300">Email</label>
            <input
              type="email"
              className="input-field"
              placeholder="you@example.com"
              {...register("email", { required: "Email is required" })}
            />
            {errors.email && <p className="mt-1 text-xs text-red-400">{errors.email.message}</p>}
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-300">Password</label>
            <input
              type="password"
              className="input-field"
              placeholder="At least 8 characters"
              {...register("password", { required: "Password is required", minLength: { value: 8, message: "Minimum 8 characters" } })}
            />
            {errors.password && <p className="mt-1 text-xs text-red-400">{errors.password.message}</p>}
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-300">Confirm password</label>
            <input
              type="password"
              className="input-field"
              placeholder="Repeat your password"
              {...register("confirm_password", {
                required: "Please confirm your password",
                validate: (value) => value === watch("password") || "Passwords do not match",
              })}
            />
            {errors.confirm_password && <p className="mt-1 text-xs text-red-400">{errors.confirm_password.message}</p>}
          </div>
          <button type="submit" disabled={isSubmitting} className="btn-primary w-full">
            {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
            Create account
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-accent-light hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
