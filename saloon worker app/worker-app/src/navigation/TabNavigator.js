import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Home, ClipboardList, CheckSquare, IndianRupee, User } from 'lucide-react-native';
import { COLORS } from '../constants/theme';

import HomeScreen from '../screens/HomeScreen';
import EarningsScreen from '../screens/EarningsScreen';
import { ActiveScreen, CompletedScreen, ProfileScreen } from '../screens/PlaceholderScreens';

const Tab = createBottomTabNavigator();

export default function TabNavigator() {
    return (
        <Tab.Navigator
            screenOptions={({ route }) => ({
                tabBarIcon: ({ focused, color, size }) => {
                    let IconComponent;

                    if (focused) {
                        size = size + 2;
                    }

                    switch (route.name) {
                        case 'Home':
                            IconComponent = Home;
                            break;
                        case 'Active':
                            IconComponent = ClipboardList;
                            break;
                        case 'Completed':
                            IconComponent = CheckSquare;
                            break;
                        case 'Earnings':
                            IconComponent = IndianRupee;
                            break;
                        case 'Profile':
                            IconComponent = User;
                            break;
                        default:
                            IconComponent = Home;
                    }

                    return <IconComponent size={size} color={color} />;
                },
                tabBarActiveTintColor: COLORS.primary,
                tabBarInactiveTintColor: COLORS.textSecondary,
                tabBarStyle: {
                    borderTopWidth: 1,
                    borderTopColor: COLORS.surface,
                    height: 60,
                    paddingBottom: 10,
                },
                headerShown: false,
            })}
        >
            <Tab.Screen name="Home" component={HomeScreen} />
            <Tab.Screen name="Active" component={ActiveScreen} />
            <Tab.Screen name="Completed" component={CompletedScreen} />
            <Tab.Screen name="Earnings" component={EarningsScreen} />
            <Tab.Screen name="Profile" component={ProfileScreen} />
        </Tab.Navigator>
    );
}
