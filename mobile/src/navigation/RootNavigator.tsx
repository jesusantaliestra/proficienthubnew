import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuth } from '../contexts/AuthContext';
import { useWhiteLabel } from '../contexts/WhiteLabelContext';
import { useTheme } from '../contexts/ThemeContext';

// Screens
import SplashScreen from '../screens/SplashScreen';
import LoginScreen from '../screens/LoginScreen';
import InstitutionSelectScreen from '../screens/InstitutionSelectScreen';
import MainTabs from './MainTabs';

export type RootStackParamList = {
  Splash: undefined;
  InstitutionSelect: undefined;
  Login: undefined;
  Main: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

const RootNavigator: React.FC = () => {
  const { user, loading: authLoading } = useAuth();
  const { loading: whiteLabelLoading } = useWhiteLabel();
  const { theme } = useTheme();

  if (authLoading || whiteLabelLoading) {
    return <SplashScreen />;
  }

  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: theme.colors.background },
      }}
    >
      {!user ? (
        <>
          <Stack.Screen name="InstitutionSelect" component={InstitutionSelectScreen} />
          <Stack.Screen name="Login" component={LoginScreen} />
        </>
      ) : (
        <Stack.Screen name="Main" component={MainTabs} />
      )}
    </Stack.Navigator>
  );
};

export default RootNavigator;