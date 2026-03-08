import React, { useState, useEffect, useCallback } from 'react';
import {
    View, Text, StyleSheet, SafeAreaView, StatusBar,
    ScrollView, ActivityIndicator, TouchableOpacity, RefreshControl
} from 'react-native';
import { COLORS, SPACING } from '../constants/theme';
import { API_BASE_URL } from '../constants/api';
import { TrendingUp, Award, Calendar, DollarSign } from 'lucide-react-native';
import { LinearGradient } from 'expo-linear-gradient';

export default function EarningsScreen({ route }) {
    const workerId = route?.params?.workerId || 1;
    const [earnings, setEarnings] = useState(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    const fetchEarnings = useCallback(async () => {
        try {
            const resp = await fetch(`${API_BASE_URL}/worker/earnings/${workerId}`);
            const data = await resp.json();
            if (data.status === 'success') {
                setEarnings(data);
            }
        } catch (err) {
            console.error("Fetch earnings error:", err);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, [workerId]);

    useEffect(() => {
        fetchEarnings();
    }, [fetchEarnings]);

    const onRefresh = () => {
        setRefreshing(true);
        fetchEarnings();
    };

    const maxAmount = earnings?.daily_chart
        ? Math.max(...earnings.daily_chart.map(d => d.amount), 1)
        : 1;

    if (loading) {
        return (
            <SafeAreaView style={styles.container}>
                <ActivityIndicator size="large" color={COLORS.primary} style={{ marginTop: 80 }} />
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={styles.container}>
            <StatusBar barStyle="light-content" />
            <ScrollView
                showsVerticalScrollIndicator={false}
                refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
            >
                {/* Header Gradient Banner */}
                <LinearGradient
                    colors={['#dc2743', '#cc2366', '#bc1888']}
                    style={styles.headerBanner}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 1 }}
                >
                    <Text style={styles.headerTitle}>My Earnings</Text>
                    <Text style={styles.todayLabel}>Today's Income</Text>
                    <Text style={styles.todayAmount}>₹{earnings?.today?.toFixed(0) || '0'}</Text>
                    <View style={styles.jobsBadge}>
                        <Award size={14} color={COLORS.white} />
                        <Text style={styles.jobsBadgeText}>{earnings?.completed_jobs || 0} Jobs Completed</Text>
                    </View>
                </LinearGradient>

                {/* Summary Cards Row */}
                <View style={styles.summaryRow}>
                    <View style={styles.summaryCard}>
                        <Calendar size={20} color={COLORS.primary} />
                        <Text style={styles.summaryAmount}>₹{earnings?.this_week?.toFixed(0) || '0'}</Text>
                        <Text style={styles.summaryLabel}>This Week</Text>
                    </View>
                    <View style={styles.summaryCard}>
                        <TrendingUp size={20} color='#10b981' />
                        <Text style={[styles.summaryAmount, { color: '#10b981' }]}>₹{earnings?.this_month?.toFixed(0) || '0'}</Text>
                        <Text style={styles.summaryLabel}>This Month</Text>
                    </View>
                    <View style={styles.summaryCard}>
                        <DollarSign size={20} color='#f59e0b' />
                        <Text style={[styles.summaryAmount, { color: '#f59e0b' }]}>₹{earnings?.total?.toFixed(0) || '0'}</Text>
                        <Text style={styles.summaryLabel}>All Time</Text>
                    </View>
                </View>

                {/* Last 7 Days Bar Chart */}
                <View style={styles.chartSection}>
                    <Text style={styles.chartTitle}>Last 7 Days Activity</Text>
                    <View style={styles.barChart}>
                        {(earnings?.daily_chart || []).map((item, index) => {
                            const barHeight = maxAmount > 0
                                ? Math.max((item.amount / maxAmount) * 120, item.amount > 0 ? 8 : 3)
                                : 3;
                            const isToday = index === 6;
                            return (
                                <View key={index} style={styles.barContainer}>
                                    <Text style={styles.barAmount}>
                                        {item.amount > 0 ? `₹${item.amount}` : ''}
                                    </Text>
                                    <View style={[
                                        styles.bar,
                                        { height: barHeight },
                                        isToday && { backgroundColor: COLORS.primary }
                                    ]} />
                                    <Text style={[styles.barLabel, isToday && { color: COLORS.primary, fontWeight: 'bold' }]}>
                                        {item.day}
                                    </Text>
                                </View>
                            );
                        })}
                    </View>
                </View>

                {/* Tips Section */}
                <View style={styles.tipCard}>
                    <Text style={styles.tipTitle}>💡 Earn More Tips</Text>
                    <Text style={styles.tipText}>• Accept bookings quickly during peak hours</Text>
                    <Text style={styles.tipText}>• Keep your profile photo & skills updated</Text>
                    <Text style={styles.tipText}>• Complete services on time for great ratings</Text>
                </View>

                <View style={{ height: 100 }} />
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f8f9fa',
    },
    headerBanner: {
        padding: 30,
        paddingTop: 50,
        alignItems: 'center',
        borderBottomLeftRadius: 30,
        borderBottomRightRadius: 30,
    },
    headerTitle: {
        color: 'rgba(255,255,255,0.8)',
        fontSize: 14,
        fontWeight: '600',
        letterSpacing: 1,
        textTransform: 'uppercase',
        marginBottom: 20,
    },
    todayLabel: {
        color: 'rgba(255,255,255,0.7)',
        fontSize: 12,
        fontWeight: '500',
    },
    todayAmount: {
        color: '#fff',
        fontSize: 52,
        fontWeight: '900',
        marginVertical: 8,
    },
    jobsBadge: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'rgba(255,255,255,0.2)',
        paddingHorizontal: 16,
        paddingVertical: 6,
        borderRadius: 20,
        marginTop: 8,
    },
    jobsBadgeText: {
        color: '#fff',
        fontSize: 13,
        fontWeight: '700',
        marginLeft: 6,
    },
    summaryRow: {
        flexDirection: 'row',
        padding: 20,
        gap: 12,
    },
    summaryCard: {
        flex: 1,
        backgroundColor: '#fff',
        borderRadius: 16,
        padding: 14,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.06,
        shadowRadius: 8,
        elevation: 3,
    },
    summaryAmount: {
        fontSize: 18,
        fontWeight: '800',
        color: COLORS.primary,
        marginTop: 8,
    },
    summaryLabel: {
        fontSize: 10,
        color: '#999',
        marginTop: 4,
        textTransform: 'uppercase',
        fontWeight: '600',
    },
    chartSection: {
        backgroundColor: '#fff',
        marginHorizontal: 20,
        borderRadius: 20,
        padding: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.06,
        shadowRadius: 8,
        elevation: 3,
        marginBottom: 20,
    },
    chartTitle: {
        fontSize: 16,
        fontWeight: '700',
        color: '#222',
        marginBottom: 20,
    },
    barChart: {
        flexDirection: 'row',
        alignItems: 'flex-end',
        justifyContent: 'space-between',
        height: 160,
    },
    barContainer: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'flex-end',
    },
    bar: {
        width: 28,
        backgroundColor: '#e0e0e0',
        borderRadius: 6,
        marginBottom: 6,
    },
    barAmount: {
        fontSize: 8,
        color: COLORS.primary,
        fontWeight: '700',
        marginBottom: 4,
        textAlign: 'center',
    },
    barLabel: {
        fontSize: 11,
        color: '#999',
        fontWeight: '600',
    },
    tipCard: {
        backgroundColor: '#fff7ed',
        marginHorizontal: 20,
        borderRadius: 16,
        padding: 20,
        borderLeftWidth: 4,
        borderLeftColor: '#f59e0b',
    },
    tipTitle: {
        fontSize: 15,
        fontWeight: '700',
        color: '#92400e',
        marginBottom: 10,
    },
    tipText: {
        fontSize: 13,
        color: '#78350f',
        marginBottom: 6,
        lineHeight: 20,
    },
});
