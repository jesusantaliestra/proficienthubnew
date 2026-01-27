import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';

// Screens
import HomeScreen from '../screens/HomeScreen';
import ExamsScreen from '../screens/ExamsScreen';
import ExamStartScreen from '../screens/ExamStartScreen';
import MaterialsScreen from '../screens/MaterialsScreen';
import ProgressScreen from '../screens/ProgressScreen';
import ProfileScreen from '../screens/ProfileScreen';
import AITutorScreen from '../screens/AITutorScreen';
import LiveClassesScreen from '../screens/LiveClassesScreen';

export type MainTabParamList = {
  Home: undefined;
  Exams: undefined;
  AITutor: undefined;
  Classes: undefined;
  Profile: undefined;
};

const Tab = createBottomTabNavigator<MainTabParamList>();
const Stack = createNativeStackNavigator();

// Exams Stack Navigator
const ExamsStack: React.FC = () => {
  const { theme } = useTheme();
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="ExamsList" component={ExamsScreen} />
      <Stack.Screen name="ExamStart" component={ExamStartScreen} />
    </Stack.Navigator>
  );
};

const MainTabs: React.FC = () => {
  const { theme } = useTheme();
  const { user } = useAuth();

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarStyle: {
          backgroundColor: theme.colors.surface,
          borderTopColor: theme.colors.border,
          paddingBottom: 8,
          paddingTop: 8,
          height: 70,
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.textSecondary,
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
        },
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          switch (route.name) {
            case 'Home':
              iconName = focused ? 'home' : 'home-outline';
              break;
            case 'Exams':
              iconName = focused ? 'document-text' : 'document-text-outline';
              break;
            case 'AITutor':
              iconName = focused ? 'chatbubbles' : 'chatbubbles-outline';
              break;
            case 'Classes':
              iconName = focused ? 'videocam' : 'videocam-outline';
              break;
            case 'Profile':
              iconName = focused ? 'person' : 'person-outline';
              break;
            default:
              iconName = 'help-outline';
          }

          return <Ionicons name={iconName} size={24} color={color} />;
        },
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} options={{ tabBarLabel: 'Inicio' }} />
      <Tab.Screen name="Exams" component={ExamsStack} options={{ tabBarLabel: 'Exámenes' }} />
      <Tab.Screen name="AITutor" component={AITutorScreen} options={{ tabBarLabel: 'AI Tutor' }} />
      <Tab.Screen name="Classes" component={LiveClassesScreen} options={{ tabBarLabel: 'Clases' }} />
      <Tab.Screen name="Profile" component={ProfileScreen} options={{ tabBarLabel: 'Perfil' }} />
    </Tab.Navigator>
  );
};

export default MainTabs;