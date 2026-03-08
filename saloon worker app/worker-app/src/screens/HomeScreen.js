import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, FlatList, SafeAreaView, StatusBar, Alert, RefreshControl, Image, TouchableOpacity, ScrollView, Switch } from 'react-native';
import { COLORS, SPACING } from '../constants/theme';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { User, Scissors, Clock, Bell } from 'lucide-react-native';
import { API_BASE_URL } from '../constants/api';

const BookingCard = ({ booking, onAccept, onReject }) => (
    <Card style={styles.bookingCard}>
        <View style={styles.cardHeader}>
            <View style={styles.infoRow}>
                <User size={20} color={COLORS.primary} />
                <Text style={styles.customerName}>{booking.user}</Text>
            </View>
            <View style={styles.statusBadge}>
                <Text style={styles.statusText}>{booking.status}</Text>
            </View>
        </View>

        <View style={styles.detailsContainer}>
            <View style={styles.detailItem}>
                <Scissors size={18} color={COLORS.textSecondary} />
                <Text style={styles.detailText}>{booking.service}</Text>
            </View>
            <View style={styles.detailItem}>
                <Clock size={18} color={COLORS.textSecondary} />
                <Text style={styles.detailText}>{booking.slot_time}</Text>
            </View>
        </View>

        {booking.status === 'pending' && (
            <View style={styles.buttonGroup}>
                <Button
                    title="REJECT"
                    variant="danger"
                    style={styles.actionButton}
                    onPress={() => onReject(booking.id)}
                />
                <View style={{ width: SPACING.md }} />
                <Button
                    title="ACCEPT"
                    style={styles.actionButton}
                    onPress={() => onAccept(booking.id)}
                />
            </View>
        )}
    </Card>
);

export default function HomeScreen({ route }) {
    const [bookings, setBookings] = useState([]);
    const [refreshing, setRefreshing] = useState(false);
    const [workerInfo, setWorkerInfo] = useState(null);
    const [isOnline, setIsOnline] = useState(false);
    const [activeTab, setActiveTab] = useState('All');
    const workerId = route?.params?.workerId || 1;

    const fetchWorkerInfo = useCallback(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/worker/${workerId}`);
            const data = await response.json();
            if (data.status !== 'error') {
                setWorkerInfo(data);
                setIsOnline(data.status === 'online');
            }
        } catch (error) {
            console.error("Fetch worker error:", error);
        }
    }, [workerId]);

    const handleToggleStatus = async () => {
        try {
            const resp = await fetch(`${API_BASE_URL}/worker/${workerId}/toggle-status`, { method: 'POST' });
            const data = await resp.json();
            if (data.status === 'success') {
                setIsOnline(data.worker_status === 'online');
            }
        } catch (err) {
            Alert.alert('Error', 'Could not update status');
        }
    };

    const fetchBookings = useCallback(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/worker/bookings/${workerId}`);
            const data = await response.json();
            setBookings(data);
        } catch (error) {
            console.error("Fetch error:", error);
        }
    }, [workerId]);

    useEffect(() => {
        fetchWorkerInfo();
        fetchBookings();
    }, [fetchWorkerInfo, fetchBookings]);

    const stats = {
        total: bookings.length,
        pending: bookings.filter(b => b.status === 'pending').length,
        completed: bookings.filter(b => b.status === 'completed').length,
    };

    const handleAccept = async (id) => {
        try {
            const response = await fetch(`${API_BASE_URL}/worker/booking/${id}/accept`, { method: 'POST' });
            if (response.ok) {
                Alert.alert("Success", "Booking Accepted. Ask client for OTP when service is done.");
                fetchBookings();
            }
        } catch (error) {
            Alert.alert("Error", "Action failed");
        }
    };

    const handleReject = async (id) => {
        Alert.alert(
            "Reject Booking",
            "Are you sure you want to reject this request?",
            [
                { text: "Cancel", style: "cancel" },
                {
                    text: "Reject",
                    style: "destructive",
                    onPress: async () => {
                        try {
                            const response = await fetch(`${API_BASE_URL}/worker/booking/${id}/reject`, { method: 'POST' });
                            if (response.ok) {
                                Alert.alert("Success", "Booking rejected");
                                fetchBookings();
                            }
                        } catch (error) {
                            Alert.alert("Error", "Action failed");
                        }
                    }
                }
            ]
        );
    };

    const handleVerifyOTP = (id) => {
        Alert.prompt(
            "Verify OTP",
            "Enter the 4-digit OTP provided by the customer",
            [
                { text: "Cancel", style: "cancel" },
                {
                    text: "Verify",
                    onPress: async (otp) => {
                        try {
                            const response = await fetch(`${API_BASE_URL}/worker/booking/${id}/verify-otp`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ otp })
                            });
                            if (response.ok) {
                                Alert.alert("Success", "Service Completed!");
                                fetchBookings();
                            } else {
                                Alert.alert("Error", "Invalid OTP");
                            }
                        } catch (e) {
                            Alert.alert("Error", "Verification failed");
                        }
                    }
                }
            ],
            "plain-text"
        );
    };

    const renderItem = ({ item }) => (
        <Card style={styles.bookingCard}>
            <View style={styles.cardHeader}>
                <View style={styles.infoRow}>
                    <User size={20} color={COLORS.primary} />
                    <Text style={styles.customerName}>{item.user}</Text>
                </View>
                <View style={[styles.statusBadge, { backgroundColor: item.status === 'completed' ? '#E8F5E9' : '#FFF4E5' }]}>
                    <Text style={[styles.statusText, { color: item.status === 'completed' ? '#2E7D32' : '#D97706' }]}>
                        {item.status.toUpperCase()}
                    </Text>
                </View>
            </View>

            <View style={styles.detailsContainer}>
                <View style={styles.detailItem}>
                    <Scissors size={18} color={COLORS.textSecondary} />
                    <Text style={styles.detailText}>{item.service}</Text>
                </View>
                <View style={styles.detailItem}>
                    <Clock size={18} color={COLORS.textSecondary} />
                    <Text style={styles.detailText}>{item.slot_time}</Text>
                </View>
            </View>

            {item.status === 'pending' && (
                <View style={styles.buttonGroup}>
                    <Button title="REJECT" variant="danger" style={styles.actionButton} onPress={() => handleReject(item.id)} />
                    <View style={{ width: SPACING.md }} />
                    <Button title="ACCEPT" style={styles.actionButton} onPress={() => handleAccept(item.id)} />
                </View>
            )}

            {item.status === 'accepted' && (
                <Button
                    title="VERIFY OTP & COMPLETE"
                    style={styles.verifyBtn}
                    onPress={() => handleVerifyOTP(item.id)}
                />
            )}
        </Card>
    );

    return (
        <SafeAreaView style={styles.container}>
            <StatusBar barStyle="dark-content" />
            <View style={styles.header}>
                <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                    {workerInfo?.image_url ? (
                        <Image source={{ uri: workerInfo.image_url }} style={styles.profileImage} />
                    ) : (
                        <View style={[styles.profileImage, { backgroundColor: COLORS.surface, justifyContent: 'center', alignItems: 'center' }]}>
                            <User size={24} color={COLORS.textSecondary} />
                        </View>
                    )}
                    <View style={{ marginLeft: SPACING.md }}>
                        <Text style={styles.headerTitle}>Hi, {workerInfo?.name || 'Worker'}</Text>
                        <Text style={styles.subtitle}>{workerInfo?.salon_name || 'Loading...'}</Text>
                    </View>
                </View>
                <TouchableOpacity onPress={() => { }}>
                    <Bell size={24} color={COLORS.primary} />
                </TouchableOpacity>
                <View style={[styles.onlineToggle, { backgroundColor: isOnline ? '#dcfce7' : '#f3f4f6' }]}>
                    <Text style={[styles.onlineText, { color: isOnline ? '#16a34a' : '#9ca3af' }]}>
                        {isOnline ? '🟢 Online' : '⚫ Offline'}
                    </Text>
                    <Switch
                        value={isOnline}
                        onValueChange={handleToggleStatus}
                        trackColor={{ false: '#e5e7eb', true: '#86efac' }}
                        thumbColor={isOnline ? '#16a34a' : '#d1d5db'}
                        style={{ transform: [{ scaleX: 0.85 }, { scaleY: 0.85 }] }}
                    />
                </View>
            </View>

            <View style={styles.statsContainer}>
                <View style={styles.statBox}>
                    <Text style={styles.statValue}>{stats.total}</Text>
                    <Text style={styles.statLabel}>Total Jobs</Text>
                </View>
                <View style={styles.statBox}>
                    <Text style={[styles.statValue, { color: COLORS.primary }]}>{stats.pending}</Text>
                    <Text style={styles.statLabel}>Pending</Text>
                </View>
                <View style={styles.statBox}>
                    <Text style={[styles.statValue, { color: '#2E7D32' }]}>{stats.completed}</Text>
                    <Text style={styles.statLabel}>Done</Text>
                </View>
            </View>

            <View style={{ paddingHorizontal: SPACING.md, marginBottom: SPACING.sm }}>
                <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.tabsContainer}>
                    {['All', 'Pending', 'Accepted', 'Completed'].map((tab) => (
                        <TouchableOpacity
                            key={tab}
                            style={[styles.tabButton, activeTab === tab && styles.tabButtonActive]}
                            onPress={() => setActiveTab(tab)}
                        >
                            <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>
                                {tab}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </ScrollView>
            </View>

            <FlatList
                data={activeTab === 'All' ? bookings : bookings.filter(b => b.status.toLowerCase() === activeTab.toLowerCase())}
                keyExtractor={(item) => item.id.toString()}
                renderItem={renderItem}
                contentContainerStyle={styles.listContent}
                refreshControl={<RefreshControl refreshing={refreshing} onRefresh={fetchBookings} />}
                ListEmptyComponent={
                    <View style={styles.emptyState}>
                        <Scissors size={60} color="#E5E7EB" style={{ marginBottom: 15 }} />
                        <Text style={styles.emptyText}>No bookings scheduled yet</Text>
                    </View>
                }
            />
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: SPACING.lg,
        paddingVertical: SPACING.md,
        backgroundColor: COLORS.white,
    },
    profileImage: {
        width: 50,
        height: 50,
        borderRadius: 25,
    },
    headerTitle: {
        fontSize: 24,
        fontWeight: '800',
        color: COLORS.text,
    },
    subtitle: {
        fontSize: 14,
        color: COLORS.textSecondary,
    },
    tabsContainer: {
        flexDirection: 'row',
        paddingBottom: SPACING.xs,
        paddingTop: SPACING.xs,
    },
    tabButton: {
        paddingVertical: 8,
        paddingHorizontal: 20,
        borderRadius: 50,
        borderWidth: 2,
        borderColor: COLORS.border,
        backgroundColor: COLORS.white,
        marginRight: SPACING.sm,
    },
    tabButtonActive: {
        backgroundColor: COLORS.primary,
        borderColor: COLORS.primary,
    },
    tabText: {
        fontSize: 14,
        fontWeight: '700',
        color: COLORS.textSecondary,
    },
    tabTextActive: {
        color: COLORS.white,
    },
    statsContainer: {
        flexDirection: 'row',
        padding: SPACING.lg,
        gap: SPACING.md,
    },
    statBox: {
        flex: 1,
        backgroundColor: COLORS.white,
        padding: SPACING.md,
        borderRadius: 16,
        alignItems: 'center',
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.05,
        shadowRadius: 5,
        elevation: 2,
    },
    statValue: {
        fontSize: 20,
        fontWeight: '800',
        color: COLORS.black,
    },
    statLabel: {
        fontSize: 10,
        color: COLORS.textSecondary,
        textTransform: 'uppercase',
        marginTop: 4,
        fontWeight: '600',
    },
    listContent: {
        padding: SPACING.lg,
        paddingTop: 0,
    },
    bookingCard: {
        marginBottom: SPACING.lg,
        padding: SPACING.lg,
        borderRadius: 20,
    },
    cardHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: SPACING.md,
    },
    infoRow: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    customerName: {
        fontSize: 18,
        fontWeight: '700',
        color: COLORS.text,
        marginLeft: SPACING.sm,
    },
    statusBadge: {
        paddingHorizontal: 10,
        paddingVertical: 4,
        borderRadius: 8,
    },
    statusText: {
        fontWeight: '800',
        fontSize: 10,
    },
    detailsContainer: {
        marginBottom: SPACING.lg,
    },
    detailItem: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: SPACING.xs,
    },
    detailText: {
        fontSize: 15,
        color: COLORS.textSecondary,
        marginLeft: SPACING.sm,
    },
    buttonGroup: {
        flexDirection: 'row',
    },
    actionButton: {
        flex: 1,
        height: 48,
        borderRadius: 12,
    },
    verifyBtn: {
        height: 48,
        borderRadius: 12,
    },
    emptyState: {
        alignItems: 'center',
        marginTop: 60,
    },
    emptyText: {
        color: COLORS.textSecondary,
        fontSize: 16,
        fontWeight: '500',
    },
    onlineToggle: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 10,
        paddingVertical: 4,
        borderRadius: 20,
        marginLeft: 10,
    },
    onlineText: {
        fontSize: 11,
        fontWeight: '700',
        marginRight: 4,
    },
});
