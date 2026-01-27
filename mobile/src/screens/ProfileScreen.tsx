import React from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Image, Switch } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { useWhiteLabel } from '../contexts/WhiteLabelContext';
import { useAuth } from '../contexts/AuthContext';

const ProfileScreen: React.FC = () => {
  const { theme, isDark, toggleTheme } = useTheme();
  const { config } = useWhiteLabel();
  const { user, logout } = useAuth();

  const MenuItem = ({ icon, label, onPress, rightElement }: {
    icon: string;
    label: string;
    onPress?: () => void;
    rightElement?: React.ReactNode;
  }) => (
    <TouchableOpacity
      style={[styles.menuItem, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}
      onPress={onPress}
      disabled={!onPress}
    >
      <View style={[styles.menuIcon, { backgroundColor: theme.colors.primary + '20' }]}>
        <Ionicons name={icon as any} size={20} color={theme.colors.primary} />
      </View>
      <Text style={[styles.menuLabel, { color: theme.colors.text }]}>{label}</Text>
      {rightElement || <Ionicons name="chevron-forward" size={20} color={theme.colors.textSecondary} />}
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Profile Header */}
        <View style={[styles.profileCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
          <View style={[styles.avatar, { backgroundColor: theme.colors.primary }]}>
            <Text style={styles.avatarText}>{user?.name?.charAt(0) || 'U'}</Text>
          </View>
          <Text style={[styles.userName, { color: theme.colors.text }]}>{user?.name || 'User'}</Text>
          <Text style={[styles.userEmail, { color: theme.colors.textSecondary }]}>{user?.email}</Text>
          {user?.institutionName && (
            <View style={[styles.institutionBadge, { backgroundColor: theme.colors.primary + '20' }]}>
              <Ionicons name="school" size={14} color={theme.colors.primary} />
              <Text style={[styles.institutionText, { color: theme.colors.primary }]}>{user.institutionName}</Text>
            </View>
          )}
        </View>

        {/* Settings Section */}
        <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>Settings</Text>
        
        <MenuItem
          icon="moon"
          label="Dark Mode"
          rightElement={
            <Switch
              value={isDark}
              onValueChange={toggleTheme}
              trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
            />
          }
        />
        <MenuItem icon="notifications-outline" label="Notifications" onPress={() => {}} />
        <MenuItem icon="language-outline" label="Language" onPress={() => {}} />
        <MenuItem icon="cloud-download-outline" label="Offline Settings" onPress={() => {}} />

        {/* Account Section */}
        <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>Account</Text>
        
        <MenuItem icon="person-outline" label="Edit Profile" onPress={() => {}} />
        <MenuItem icon="lock-closed-outline" label="Change Password" onPress={() => {}} />
        <MenuItem icon="help-circle-outline" label="Help & Support" onPress={() => {}} />
        <MenuItem icon="document-text-outline" label="Terms of Service" onPress={() => {}} />

        {/* Logout */}
        <TouchableOpacity
          style={[styles.logoutBtn, { backgroundColor: theme.colors.accent + '10' }]}
          onPress={logout}
        >
          <Ionicons name="log-out-outline" size={20} color={theme.colors.accent} />
          <Text style={[styles.logoutText, { color: theme.colors.accent }]}>Log Out</Text>
        </TouchableOpacity>

        {/* Footer */}
        {config.showPoweredBy && (
          <View style={styles.footer}>
            <Text style={[styles.footerText, { color: theme.colors.textSecondary }]}>
              Powered by ProficientHub
            </Text>
            <Text style={[styles.versionText, { color: theme.colors.textSecondary }]}>v1.0.0</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
  },
  profileCard: {
    alignItems: 'center',
    padding: 24,
    borderRadius: 16,
    borderWidth: 1,
    marginBottom: 24,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  avatarText: {
    color: '#FFFFFF',
    fontSize: 32,
    fontWeight: 'bold',
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  userEmail: {
    fontSize: 14,
    marginTop: 4,
  },
  institutionBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginTop: 12,
    gap: 6,
  },
  institutionText: {
    fontWeight: '600',
    fontSize: 12,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 12,
    marginTop: 8,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 8,
  },
  menuIcon: {
    width: 36,
    height: 36,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  menuLabel: {
    flex: 1,
    marginLeft: 12,
    fontSize: 16,
    fontWeight: '500',
  },
  logoutBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    marginTop: 16,
    gap: 8,
  },
  logoutText: {
    fontSize: 16,
    fontWeight: '600',
  },
  footer: {
    alignItems: 'center',
    marginTop: 32,
  },
  footerText: {
    fontSize: 12,
  },
  versionText: {
    fontSize: 10,
    marginTop: 4,
  },
});

export default ProfileScreen;