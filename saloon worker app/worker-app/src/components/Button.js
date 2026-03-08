import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { COLORS, SIZES, SPACING } from '../constants/theme';

export const Button = ({ title, onPress, variant = 'primary', loading = false, style, textStyle }) => {
    return (
        <TouchableOpacity
            onPress={onPress}
            disabled={loading}
            style={[
                styles.button,
                styles[variant],
                style,
                loading && styles.disabled
            ]}
        >
            {loading ? (
                <ActivityIndicator color={variant === 'primary' ? COLORS.white : COLORS.primary} />
            ) : (
                <Text style={[styles.text, styles[`${variant}Text`], textStyle]}>{title}</Text>
            )}
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    button: {
        height: SIZES.buttonHeight,
        borderRadius: SIZES.radius,
        justifyContent: 'center',
        alignItems: 'center',
        paddingHorizontal: SPACING.lg,
        flexDirection: 'row',
    },
    primary: {
        backgroundColor: COLORS.primary,
    },
    secondary: {
        backgroundColor: COLORS.white,
        borderWidth: 1,
        borderColor: COLORS.primary,
    },
    outline: {
        backgroundColor: 'transparent',
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    danger: {
        backgroundColor: COLORS.error,
    },
    text: {
        fontSize: 16,
        fontWeight: '600',
    },
    primaryText: {
        color: COLORS.white,
    },
    secondaryText: {
        color: COLORS.primary,
    },
    outlineText: {
        color: COLORS.text,
    },
    dangerText: {
        color: COLORS.white,
    },
    disabled: {
        opacity: 0.6,
    },
});
