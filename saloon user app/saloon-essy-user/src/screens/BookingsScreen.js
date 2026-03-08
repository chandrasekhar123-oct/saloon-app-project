import React, { useEffect, useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    FlatList,
    Image,
    TouchableOpacity,
    SafeAreaView
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SHADOW } from '../constants/theme';
import { API_BASE_URL } from '../constants/api';

export default function BookingsScreen({ setScreen }) {
    const [bookings, setBookings] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchBookings();
    }, []);

    const fetchBookings = async () => {
        try {
            const resp = await fetch(`${API_BASE_URL}/user/booking/1`); // Hardcoded user ID for demo
            const data = await resp.json();
            setBookings(data);
        } catch (err) {
            console.log(err);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status.toLowerCase()) {
            case 'completed': return COLORS.success;
            case 'accepted': return '#3B82F6';
            case 'pending': return '#F59E0B';
            default: return COLORS.textSecondary;
        }
    };

    const renderBookingCard = ({ item }) => (
        <View style={styles.card}>
            <View style={styles.cardHeader}>
                <View>
                    <Text style={styles.idText}>Booking #{item.id}</Text>
                    <Text style={styles.dateText}>{item.slot_time}</Text>
                </View>
                <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) + '20' }]}>
                    <Text style={[styles.statusText, { color: getStatusColor(item.status) }]}>{item.status.toUpperCase()}</Text>
                </View>
            </View>

            <View style={styles.cardBody}>
                <View style={styles.infoRow}>
                    <Ionicons name="storefront-outline" size={16} color={COLORS.textSecondary} />
                    <Text style={styles.infoText}>{item.salon}</Text>
                </View>
                <View style={styles.infoRow}>
                    <Ionicons name="cut-outline" size={16} color={COLORS.textSecondary} />
                    <Text style={styles.infoText}>{item.service}</Text>
                </View>
            </View>

            {item.status.toLowerCase() === 'accepted' && (
                <View style={styles.otpSection}>
                    <Text style={styles.otpLabel}>Show OTP to Specialist:</Text>
                    <Text style={styles.otpValue}>{item.otp}</Text>
                </View>
            )}

            {item.status.toLowerCase() === 'completed' && (
                <TouchableOpacity style={styles.reviewBtn} onPress={() => setScreen('review')}>
                    <Text style={styles.reviewBtnText}>Rate Experience</Text>
                </TouchableOpacity>
            )}
        </View>
    );

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.headerTitle}>My Bookings</Text>
            </View>

            {bookings.length === 0 && !loading ? (
                <View style={styles.emptyState}>
                    <Ionicons name="calendar-outline" size={80} color="#E5E7EB" />
                    <Text style={styles.emptyTitle}>No Bookings Yet</Text>
                    <Text style={styles.emptySubtitle}>Your upcoming salon appointments will appear here.</Text>
                    <TouchableOpacity style={styles.bookNowBtn} onPress={() => setScreen('home')}>
                        <Text style={styles.bookNowText}>Book Now</Text>
                    </TouchableOpacity>
                </View>
            ) : (
                <FlatList
                    data={bookings}
                    keyExtractor={item => item.id.toString()}
                    renderItem={renderBookingCard}
                    contentContainerStyle={{ padding: 20 }}
                    refreshing={loading}
                    onRefresh={fetchBookings}
                />
            )}
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    header: {
        padding: 20,
        backgroundColor: COLORS.white,
        borderBottomWidth: 1,
        borderBottomColor: '#F3F4F6',
    },
    headerTitle: {
        fontSize: 22,
        fontWeight: '800',
        color: COLORS.text,
    },
    card: {
        backgroundColor: COLORS.white,
        borderRadius: 15,
        padding: 15,
        marginBottom: 15,
        ...SHADOW,
    },
    cardHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        borderBottomWidth: 1,
        borderBottomColor: '#F3F4F6',
        paddingBottom: 12,
    },
    idText: {
        fontSize: 12,
        color: COLORS.textSecondary,
        fontWeight: '600',
    },
    dateText: {
        fontSize: 14,
        color: COLORS.text,
        fontWeight: '700',
        marginTop: 2,
    },
    statusBadge: {
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 6,
    },
    statusText: {
        fontSize: 10,
        fontWeight: '800',
    },
    cardBody: {
        paddingVertical: 12,
    },
    infoRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 6,
    },
    infoText: {
        fontSize: 14,
        color: COLORS.text,
        marginLeft: 10,
        fontWeight: '500',
    },
    otpSection: {
        backgroundColor: '#F3F4F6',
        padding: 12,
        borderRadius: 10,
        alignItems: 'center',
    },
    otpLabel: {
        fontSize: 11,
        color: COLORS.textSecondary,
        marginBottom: 5,
    },
    otpValue: {
        fontSize: 24,
        fontWeight: '800',
        color: COLORS.primary,
        letterSpacing: 4,
    },
    reviewBtn: {
        marginTop: 5,
        backgroundColor: '#F3F4F6',
        paddingVertical: 10,
        borderRadius: 8,
        alignItems: 'center',
    },
    reviewBtnText: {
        fontSize: 13,
        fontWeight: '700',
        color: COLORS.text,
    },
    emptyState: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingHorizontal: 40,
    },
    emptyTitle: {
        fontSize: 20,
        fontWeight: '700',
        color: COLORS.text,
        marginTop: 20,
    },
    emptySubtitle: {
        fontSize: 14,
        color: COLORS.textSecondary,
        textAlign: 'center',
        marginTop: 8,
    },
    bookNowBtn: {
        marginTop: 25,
        backgroundColor: COLORS.primary,
        paddingHorizontal: 30,
        paddingVertical: 14,
        borderRadius: 12,
    },
    bookNowText: {
        color: COLORS.white,
        fontWeight: 'bold',
    },
});
