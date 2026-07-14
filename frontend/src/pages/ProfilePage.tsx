import { useState } from "react";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";
import { isAxiosError } from "axios";
import { Loader2, Save } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { authApi } from "../api/auth";
import { PageHeader } from "../components/Shared";

interface ProfileForm {
  full_name: string;
}

interface PasswordForm {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export function ProfilePage() {
  const { user, refreshUser } = useAuth();
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [isSavingPassword, setIsSavingPassword] = useState(false);

  const profileForm = useForm<ProfileForm>({ defaultValues: { full_name: user?.full_name ?? "" } });
  const passwordForm = useForm<PasswordForm>();

  const onSaveProfile = async (data: ProfileForm) => {
    setIsSavingProfile(true);
    try {
      await authApi.updateMe({ full_name: data.full_name });
      await refreshUser();
      toast.success("Profile updated");
    } catch {
      toast.error("Could not update profile");
    } finally {
      setIsSavingProfile(false);
    }
  };

  const onChangePassword = async (data: PasswordForm) => {
    if (data.new_password !== data.confirm_password) {
      toast.error("Passwords do not match");
      return;
    }
    setIsSavingPassword(true);
    try {
      await authApi.changePassword({ current_password: data.current_password, new_password: data.new_password });
      toast.success("Password changed");
      passwordForm.reset();
    } catch (err) {
      const message = isAxiosError(err) ? err.response?.data?.detail : "Could not change password";
      toast.error(message || "Could not change password");
    } finally {
      setIsSavingPassword(false);
    }
  };

  if (!user) return null;

  return (
    <div className="mx-auto max-w-2xl px-6 py-8">
      <PageHeader title="Profile" description="Manage your account details." />

      <form onSubmit={profileForm.handleSubmit(onSaveProfile)} className="card mb-6 space-y-4 p-6">
        <h2 className="text-sm font-semibold text-slate-100">Account details</h2>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-300">Full name</label>
          <input className="input-field" {...profileForm.register("full_name", { required: true })} />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-300">Email</label>
          <input className="input-field opacity-60" value={user.email} disabled />
        </div>
        <button type="submit" disabled={isSavingProfile} className="btn-primary">
          {isSavingProfile ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
          Save changes
        </button>
      </form>

      <form onSubmit={passwordForm.handleSubmit(onChangePassword)} className="card space-y-4 p-6">
        <h2 className="text-sm font-semibold text-slate-100">Change password</h2>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-300">Current password</label>
          <input type="password" className="input-field" {...passwordForm.register("current_password", { required: true })} />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-300">New password</label>
          <input type="password" className="input-field" {...passwordForm.register("new_password", { required: true, minLength: 8 })} />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-300">Confirm new password</label>
          <input type="password" className="input-field" {...passwordForm.register("confirm_password", { required: true })} />
        </div>
        <button type="submit" disabled={isSavingPassword} className="btn-primary">
          {isSavingPassword ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
          Update password
        </button>
      </form>
    </div>
  );
}
