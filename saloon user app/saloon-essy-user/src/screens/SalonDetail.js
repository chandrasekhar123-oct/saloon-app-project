import React, { useEffect, useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    TouchableOpacity,
    Image,
    StatusBar,
    Dimensions
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SHADOW } from '../constants/theme';
import { API_BASE_URL } from '../constants/api';

const { width } = Dimensions.get('window');

export default function SalonDetail({
    selectedSalon,
    setScreen,
    markFavorite,
    favorites,
    toggleService,
    selectedServices,
    workers,
    selectedWorker,
    setSelectedWorker,
    slots,
    selectedSlot,
    setSelectedSlot,
    selectedDate,
    setSelectedDate,
    salonTotal
}) {
    const [services, setServices] = useState([]);
    const isFavorite = favorites.includes(selectedSalon.id);

    useEffect(() => {
        fetchServices();
    }, []);

    const fetchServices = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/user/salon/${selectedSalon.id}/services`);
            const data = await response.json();
            setServices(data);
        } catch (error) {
            console.error("Error fetching services:", error);
        }
    };

    return (
        <View style={styles.container}>
            <StatusBar barStyle="light-content" />

            {/* Header Image */}
            <View style={styles.imageContainer}>
                <Image source={{ uri: selectedSalon.image_url || selectedSalon.img }} style={styles.headerImg} />
                <View style={styles.headerOverlay}>
                    <TouchableOpacity style={styles.backBtn} onPress={() => setScreen('home')}>
                        <Ionicons name="arrow-back" size={24} color={COLORS.white} />
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.backBtn} onPress={() => markFavorite(selectedSalon.id)}>
                        <Ionicons name={isFavorite ? "heart" : "heart-outline"} size={24} color={isFavorite ? COLORS.primary : COLORS.white} />
                    </TouchableOpacity>
                </View>
            </View>

            <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
                <View style={styles.infoSection}>
                    <View style={styles.titleRow}>
                        <Text style={styles.salonName}>{selectedSalon.name}</Text>
                        <View style={styles.ratingBadge}>
                            <Ionicons name="star" size={16} color="#FFD700" />
                            <Text style={styles.ratingText}>{selectedSalon.rating || '4.5'}</Text>
                        </View>
                    </View>
                    <Text style={styles.address}>{selectedSalon.address}</Text>

                    <View style={styles.metaRow}>
                        <View style={styles.metaItem}>
                            <Ionicons name="time-outline" size={16} color={COLORS.primary} />
                            <Text style={styles.metaText}>Open: 09:00 AM - 09:00 PM</Text>
                        </View>
                    </View>
                </View>

                {/* Services */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Select Services</Text>
                    {services.map(service => {
                        const isSelected = selectedServices.some(s => s.id === service.id);
                        return (
                            <TouchableOpacity
                                key={service.id}
                                style={[styles.serviceCard, isSelected && styles.selectedCard]}
                                onPress={() => toggleService(service)}
                            >
                                <Image source={{ uri: service.image_url }} style={styles.serviceImg} />
                                <View style={styles.serviceInfo}>
                                    <Text style={styles.serviceName}>{service.name}</Text>
                                    <Text style={styles.serviceDuration}>{service.duration} mins</Text>
                                    <Text style={styles.servicePrice}>₹{service.price}</Text>
                                </View>
                                <View style={[styles.checkbox, isSelected && styles.checked]}>
                                    {isSelected && <Ionicons name="checkmark" size={16} color={COLORS.white} />}
                                </View>
                            </TouchableOpacity>
                        );
                    })}
                </View>

                {/* Specialist */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Choose Specialist</Text>
                    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.workerList}>
                        {workers.map(worker => (
                            <TouchableOpacity
                                key={worker.id}
                                style={[styles.workerCard, selectedWorker?.id === worker.id && styles.selectedWorkerCard]}
                                onPress={() => setSelectedWorker(worker)}
                            >
                                <Image source={{ uri: worker.photo || worker.image_url }} style={styles.workerImg} />
                                <Text style={styles.workerName}>{worker.name}</Text>
                                <Text style={styles.workerRole}>{worker.skill || 'Expert'}</Text>
                            </TouchableOpacity>
                        ))}
                    </ScrollView>
                </View>

                {/* Slots */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Pick a Time Slot</Text>
                    <View style={styles.datePicker}>
                        <TouchableOpacity style={[styles.dateBtn, !selectedDate && styles.selectedDateBtn]} onPress={() => setSelectedDate('Today')}>
                            <Text style={[styles.dateText, !selectedDate && styles.selectedDateText]}>Today</Text>
                        </TouchableOpacity>
                        <TouchableOpacity style={[styles.dateBtn, selectedDate === 'Tomorrow' && styles.selectedDateBtn]} onPress={() => setSelectedDate('Tomorrow')}>
                            <Text style={[styles.dateText, selectedDate === 'Tomorrow' && styles.selectedDateText]}>Tomorrow</Text>
                        </TouchableOpacity>
                    </View>
                    <View style={styles.slotGrid}>
                        {slots.map(slot => (
                            <TouchableOpacity
                                key={slot}
                                style={[styles.slotBtn, selectedSlot === slot && styles.selectedSlotBtn]}
                                onPress={() => setSelectedSlot(slot)}
                            >
                                <Text style={[styles.slotText, selectedSlot === slot && styles.selectedSlotText]}>{slot}</Text>
                            </TouchableOpacity>
                        ))}
                    </View>
                </View>

                <View style={{ height: 120 }} />
            </ScrollView>

            {/* Floating Action Button */}
            {selectedServices.length > 0 && (
                <View style={styles.footer}>
                    <View>
                        <Text style={styles.footerLabel}>{selectedServices.length} ServiceSelected</Text>
                        <Text style={styles.footerPrice}>Total: ₹{salonTotal}</Text>
                    </View>
                    <TouchableOpacity
                        style={styles.bookBtn}
                        onPress={() => setScreen('summary')}
                    >
                        <Text style={styles.bookBtnText}>Review Booking</Text>
                        <Ionicons name="arrow-forward" size={20} color={COLORS.white} style={{ marginLeft: 8 }} />
                    </TouchableOpacity>
                </View>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.white,
    },
    imageContainer: {
        width: width,
        height: 300,
    },
    headerImg: {
        width: '100%',
        height: '100%',
    },
    headerOverlay: {
        position: 'absolute',
        top: 50,
        left: 0,
        right: 0,
        flexDirection: 'row',
        justifyContent: 'space-between',
        paddingHorizontal: 20,
    },
    backBtn: {
        width: 44,
        height: 44,
        borderRadius: 22,
        backgroundColor: 'rgba(0,0,0,0.3)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    content: {
        flex: 1,
        marginTop: -30,
        backgroundColor: COLORS.white,
        borderTopLeftRadius: 30,
        borderTopRightRadius: 30,
        paddingHorizontal: 20,
    },
    infoSection: {
        paddingVertical: 25,
        borderBottomWidth: 1,
        borderBottomColor: '#F3F4F6',
    },
    titleRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    salonName: {
        fontSize: 24,
        fontWeight: '800',
        color: COLORS.text,
        flex: 1,
    },
    ratingBadge: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#FFFBEB',
        paddingHorizontal: 10,
        paddingVertical: 5,
        borderRadius: 10,
    },
    ratingText: {
        marginLeft: 5,
        fontWeight: 'bold',
        color: '#D97706',
    },
    address: {
        fontSize: 14,
        color: COLORS.textSecondary,
        marginTop: 8,
    },
    metaRow: {
        flexDirection: 'row',
        marginTop: 15,
    },
    metaItem: {
        flexDirection: 'row',
        alignItems: 'center',
        marginRight: 20,
    },
    metaText: {
        fontSize: 13,
        color: COLORS.text,
        marginLeft: 6,
        fontWeight: '500',
    },
    section: {
        marginTop: 25,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: 15,
    },
    serviceCard: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#F9FAFB',
        padding: 12,
        borderRadius: 15,
        marginBottom: 12,
        borderWidth: 1,
        borderColor: '#F3F4F6',
    },
    selectedCard: {
        borderColor: COLORS.primary,
        backgroundColor: '#FFF1F2',
    },
    serviceImg: {
        width: 60,
        height: 60,
        borderRadius: 12,
    },
    serviceInfo: {
        flex: 1,
        marginLeft: 15,
    },
    serviceName: {
        fontSize: 16,
        fontWeight: '700',
        color: COLORS.text,
    },
    serviceDuration: {
        fontSize: 12,
        color: COLORS.textSecondary,
        marginTop: 2,
    },
    servicePrice: {
        fontSize: 15,
        fontWeight: 'bold',
        color: COLORS.primary,
        marginTop: 4,
    },
    checkbox: {
        width: 24,
        height: 24,
        borderRadius: 12,
        borderWidth: 2,
        borderColor: '#D1D5DB',
        justifyContent: 'center',
        alignItems: 'center',
    },
    checked: {
        backgroundColor: COLORS.primary,
        borderColor: COLORS.primary,
    },
    workerList: {
        paddingBottom: 10,
    },
    workerCard: {
        alignItems: 'center',
        marginRight: 20,
        width: 100,
    },
    selectedWorkerCard: {
        // Add extra styling for selected worker
    },
    workerImg: {
        width: 80,
        height: 80,
        borderRadius: 40,
        borderWidth: 3,
        borderColor: 'transparent',
    },
    workerName: {
        fontSize: 14,
        fontWeight: 'bold',
        color: COLORS.text,
        marginTop: 8,
    },
    workerRole: {
        fontSize: 11,
        color: COLORS.textSecondary,
    },
    datePicker: {
        flexDirection: 'row',
        gap: 10,
        marginBottom: 15,
    },
    dateBtn: {
        paddingHorizontal: 20,
        paddingVertical: 10,
        borderRadius: 10,
        backgroundColor: '#F3F4F6',
    },
    selectedDateBtn: {
        backgroundColor: COLORS.primary,
    },
    slotGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 10,
    },
    slotBtn: {
        width: '30%',
        paddingVertical: 12,
        backgroundColor: '#F3F4F6',
        borderRadius: 12,
        alignItems: 'center',
    },
    selectedSlotBtn: {
        backgroundColor: COLORS.text,
    },
    slotText: {
        fontSize: 13,
        fontWeight: '600',
        color: COLORS.text,
    },
    selectedSlotText: {
        color: COLORS.white,
    },
    footer: {
        position: 'absolute',
        bottom: 30,
        left: 20,
        right: 20,
        backgroundColor: COLORS.white,
        padding: 20,
        borderRadius: 20,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        ...SHADOW,
        shadowOpacity: 0.15,
    },
    footerLabel: {
        fontSize: 12,
        color: COLORS.textSecondary,
    },
    footerPrice: {
        fontSize: 18,
        fontWeight: '800',
        color: COLORS.text,
    },
    bookBtn: {
        backgroundColor: COLORS.primary,
        paddingHorizontal: 20,
        paddingVertical: 12,
        borderRadius: 15,
        flexDirection: 'row',
        alignItems: 'center',
    },
    bookBtnText: {
        color: COLORS.white,
        fontWeight: 'bold',
        fontSize: 15,
    },
});
