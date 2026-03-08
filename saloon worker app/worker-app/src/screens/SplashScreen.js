import React, { useEffect } from 'react';
import { View, Text, StyleSheet, Image, ActivityIndicator } from 'react-native';
import { COLORS, SPACING } from '../constants/theme';
import { Scissors } from 'lucide-react-native';
import { LinearGradient } from 'expo-linear-gradient';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function SplashScreen({ navigation }) {
    useEffect(() => {
        const checkLoginStatus = async () => {
            try {
                const workerId = await AsyncStorage.getItem('workerId');
                setTimeout(() => {
                    if (workerId) {
                        navigation.replace('Main', { workerId });
                    } else {
                        navigation.replace('Login');
                    }
                }, 2000);
            } catch (e) {
                console.error("Auth logic error:", e);
                navigation.replace('Login');
            }
        };

        checkLoginStatus();
    }, []);

    return (
        <LinearGradient
            colors={['#f09433', '#e6683c', '#dc2743', '#cc2366', '#bc1888']}
            style={styles.container}
            start={{ x: 0.0, y: 0.0 }}
            end={{ x: 1.0, y: 1.0 }}
        >
            <View style={styles.logoContainer}>
                <Scissors size={60} color={COLORS.white} />
            </View>
            <Text style={styles.appName}>SALOON ESSY</Text>
            <Text style={styles.tagline}>Manage Your Salon Jobs Easily</Text>

            <View style={styles.loader}>
                <ActivityIndicator size="large" color={COLORS.white} />
            </View>
        </LinearGradient>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    logoContainer: {
        width: 120,
        height: 120,
        borderRadius: 60,
        backgroundColor: 'rgba(255, 255, 255, 0.2)',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: SPACING.lg,
    },
    appName: {
        fontSize: 32,
        fontWeight: 'bold',
        color: COLORS.white,
        letterSpacing: 2,
    },
    tagline: {
        fontSize: 16,
        color: 'rgba(255, 255, 255, 0.8)',
        marginTop: SPACING.xs,
    },
    loader: {
        position: 'absolute',
        bottom: 100,
    },
});
