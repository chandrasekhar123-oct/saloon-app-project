import React from 'react';
import { View, StyleSheet } from 'react-native';
import { COLORS, SIZES, SPACING } from '../constants/theme';

export const Card = ({ children, style }) => {
    return (
        <View style={[styles.card, style]}>
            {children}
        </View>
    );
};

const styles = StyleSheet.create({
    card: {
        backgroundColor: COLORS.white,
        borderRadius: SIZES.radius,
        padding: SPACING.md,
        marginBottom: SPACING.md,
        // Soft shadows as requested
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 3,
    },
});
