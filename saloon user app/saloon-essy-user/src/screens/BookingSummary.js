import React from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    TouchableOpacity,
    Image,
    SafeAreaView
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SHADOW } from '../constants/theme';

export default function BookingSummary({
    selectedSalon,
    selectedServices,
    selectedWorker,
    selectedSlot,
    salonTotal,
    confirmBooking,
    paymentMethods
}) {
    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => console.log('back')}>
                    <Ionicons name="arrow-back" size={24} color={COLORS.text} />
                </TouchableOpacity>
                <Text style={styles.headerTitle}>Review Booking</Text>
                <View style={{ width: 24 }} />
            </View>

            <ScrollView style={styles.content}>
                {/* Salon Card */}
                <View style={styles.card}>
                    <Image source={{ uri: selectedSalon.image_url || selectedSalon.img }} style={styles.salonImg} />
                    <View style={styles.cardContent}>
                        <Text style={styles.salonName}>{selectedSalon.name}</Text>
                        <View style={styles.metaRow}>
                            <Ionicons name="location-outline" size={14} color={COLORS.textSecondary} />
                            <Text style={styles.metaText}>{selectedSalon.address}</Text>
                        </View>
                    </View>
                </View>

                {/* Appointment Details */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Appointment Details</Text>
                    <View style={styles.detailCard}>
                        <View style={styles.detailItem}>
                            <View style={styles.iconCircle}>
                                <Ionicons name="calendar-outline" size={20} color={COLORS.primary} />
                            </View>
                            <View style={{ marginLeft: 15 }}>
                                <Text style={styles.detailLabel}>Date & Time</Text>
                                <Text style={styles.detailValue}>Today, {selectedSlot}</Text>
                            </View>
                        </View>
                        <View style={[styles.detailItem, { marginTop: 15 }]}>
                            <View style={styles.iconCircle}>
                                <Ionicons name="person-outline" size={20} color={COLORS.primary} />
                            </View>
                            <View style={{ marginLeft: 15 }}>
                                <Text style={styles.detailLabel}>Specialist</Text>
                                <Text style={styles.detailValue}>{selectedWorker?.name || 'Any Available'}</Text>
                            </View>
                        </View>
                    </View>
                </View>

                {/* Selected Services */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Selected Services</Text>
                    <View style={styles.servicesCard}>
                        {selectedServices.map((service, index) => (
                            <View key={service.id} style={[styles.serviceRow, index !== 0 && styles.serviceDivider]}>
                                <Text style={styles.serviceName}>{service.name}</Text>
                                <Text style={styles.servicePrice}>₹{service.price}</Text>
                            </View>
                        ))}
                        <View style={styles.totalRow}>
                            <Text style={styles.totalLabel}>Total Payable</Text>
                            <Text style={styles.totalValue}>₹{salonTotal}</Text>
                        </View>
                    </View>
                </View>

                {/* Payment Method */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Payment Method</Text>
                    <TouchableOpacity style={styles.paymentCard}>
                        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                            <Ionicons name="cash-outline" size={24} color={COLORS.text} />
                            <Text style={styles.paymentText}>Cash at Salon</Text>
                        </View>
                        <Ionicons name="chevron-forward" size={20} color={COLORS.textSecondary} />
                    </TouchableOpacity>
                </View>

                <View style={{ height: 40 }} />
            </ScrollView>

            <View style={styles.footer}>
                <TouchableOpacity style={styles.confirmBtn} onPress={confirmBooking}>
                    <Text style={styles.confirmBtnText}>Confirm Appointment</Text>
                </TouchableOpacity>
            </View>
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
        padding: 20,
        backgroundColor: COLORS.white,
    },
    headerTitle: {
        fontSize: 18,
        fontWeight: '700',
        color: COLORS.text,
    },
    content: {
        padding: 20,
    },
    card: {
        backgroundColor: COLORS.white,
        borderRadius: 20,
        overflow: 'hidden',
        ...SHADOW,
    },
    salonImg: {
        width: '100%',
        height: 140,
    },
    cardContent: {
        padding: 15,
    },
    salonName: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    metaRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginTop: 5,
    },
    metaText: {
        fontSize: 13,
        color: COLORS.textSecondary,
        marginLeft: 5,
    },
    section: {
        marginTop: 25,
    },
    sectionTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: 12,
    },
    detailCard: {
        backgroundColor: COLORS.white,
        padding: 15,
        borderRadius: 15,
        ...SHADOW,
    },
    detailItem: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    iconCircle: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: '#FFF1F2',
        justifyContent: 'center',
        alignItems: 'center',
    },
    detailLabel: {
        fontSize: 12,
        color: COLORS.textSecondary,
    },
    detailValue: {
        fontSize: 15,
        fontWeight: '600',
        color: COLORS.text,
    },
    servicesCard: {
        backgroundColor: COLORS.white,
        padding: 15,
        borderRadius: 15,
        ...SHADOW,
    },
    serviceRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        paddingVertical: 10,
    },
    serviceDivider: {
        borderTopWidth: 1,
        borderTopColor: '#F3F4F6',
    },
    serviceName: {
        fontSize: 14,
        color: COLORS.text,
    },
    servicePrice: {
        fontSize: 14,
        fontWeight: '600',
        color: COLORS.text,
    },
    totalRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginTop: 15,
        paddingTop: 15,
        borderTopWidth: 2,
        borderTopColor: '#F3F4F6',
        borderStyle: 'dashed',
    },
    totalLabel: {
        fontSize: 16,
        fontWeight: '800',
        color: COLORS.text,
    },
    totalValue: {
        fontSize: 18,
        fontWeight: '800',
        color: COLORS.primary,
    },
    paymentCard: {
        backgroundColor: COLORS.white,
        padding: 18,
        borderRadius: 15,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        ...SHADOW,
    },
    paymentText: {
        fontSize: 15,
        fontWeight: '600',
        color: COLORS.text,
        marginLeft: 15,
    },
    footer: {
        padding: 20,
        backgroundColor: COLORS.white,
    },
    confirmBtn: {
        backgroundColor: COLORS.primary,
        height: 56,
        borderRadius: 16,
        justifyContent: 'center',
        alignItems: 'center',
        ...SHADOW,
        shadowColor: COLORS.primary,
    },
    confirmBtnText: {
        color: COLORS.white,
        fontSize: 16,
        fontWeight: 'bold',
    },
});
