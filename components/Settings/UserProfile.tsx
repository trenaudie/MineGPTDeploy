import { FC, useState, useEffect } from 'react';
import { SidebarButton } from '../Sidebar/SidebarButton';
import { IconUser } from '@tabler/icons-react';
import { useTranslation } from 'next-i18next';

interface UserProfile {
  email: string;
  password: string;
  numRequests: number;
  numDocuments: number;
}

interface Props {
  fetchProfile: () => Promise<UserProfile>;
  updateProfile: (profile: UserProfile) => void;
}

export const UserProfile: FC<Props> = ({ fetchProfile, updateProfile }) => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const { t } = useTranslation('sidebar');

  useEffect(() => {
    fetchProfile().then(setProfile);
  }, [fetchProfile]);

  const handleUpdate = () => {
    const updatedProfile = { ...profile, password: 'newPassword' }; // replace with actual updated data
    updateProfile(updatedProfile);
    setProfile(updatedProfile);
  };

  if (!profile) {
    return <div>Loading...</div>;
  }

  return (
    <>
      <div>Email: {profile.email}</div>
      <div>Password: {profile.password}</div>
      <div>Number of Requests: {profile.numRequests}</div>
      <div>Number of Documents: {profile.numDocuments}</div>

      <SidebarButton
        text={t('Profile')}
        icon={<IconUser size={18} />}
        onClick={handleUpdate}
      />
    </>
  );
};
