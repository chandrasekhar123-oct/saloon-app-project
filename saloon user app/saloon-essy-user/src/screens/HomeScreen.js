import React from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    TouchableOpacity,
    Image,
    TextInput,
    FlatList
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SHADOW } from '../constants/theme';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';

export default function HomeScreen({
    currentArea,
    currentCity,
    setShowLocationPicker,
    banners,
    categories,
    filteredSalons,
    handleSelectSalon,
    selectedCategory,
    setSelectedCategory,
    searchQuery,
    setSearchQuery,
    nearestCityFallback
}) {
    return (
        <LinearGradient
            colors={['#fffbfa', '#ffede8', '#ffe4dd', '#fffbfb']}
            style={styles.container}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
        >
            {/* Header */}
            <View style={styles.header}>
                <TouchableOpacity style={styles.locationContainer} onPress={() => setShowLocationPicker(true)}>
                    <Ionicons name="location" size={20} color={COLORS.primary} />
                    <View style={{ marginLeft: 8 }}>
                        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                            <Text style={styles.cityName}>{currentCity.name}</Text>
                            <Ionicons name="chevron-down" size={14} color={COLORS.text} style={{ marginLeft: 4 }} />
                        </View>
                        <Text style={styles.areaName} numberOfLines={1}>{currentArea}</Text>
                    </View>
                </TouchableOpacity>
                <TouchableOpacity style={styles.notificationBtn}>
                    <Ionicons name="notifications-outline" size={24} color={COLORS.text} />
                    <View style={styles.dot} />
                </TouchableOpacity>
            </View>

            <ScrollView showsVerticalScrollIndicator={false}>
                {/* Search Bar */}
                <View style={styles.searchSection}>
                    <View style={styles.searchBar}>
                        <Ionicons name="search" size={20} color={COLORS.textSecondary} />
                        <TextInput
                            style={styles.searchInput}
                            placeholder="Search salons, services..."
                            value={searchQuery}
                            onChangeText={setSearchQuery}
                        />
                    </View>
                </View>

                {/* Promo Banners */}
                <ScrollView
                    horizontal
                    showsHorizontalScrollIndicator={false}
                    contentContainerStyle={styles.banners}
                >
                    {banners.map(banner => (
                        <TouchableOpacity
                            key={banner.id}
                            style={[styles.bannerCard, { backgroundColor: banner.color }]}
                        >
                            <View>
                                <Text style={styles.bannerTitle}>{banner.title}</Text>
                                <Text style={styles.bannerSubtitle}>{banner.subtitle}</Text>
                                <TouchableOpacity style={styles.bannerBtn}>
                                    <Text style={styles.bannerBtnText}>Claim Now</Text>
                                </TouchableOpacity>
                            </View>
                            <Image
                                source={{ uri: 'https://cdn-icons-png.flaticon.com/512/3468/3468413.png' }}
                                style={styles.bannerImg}
                            />
                        </TouchableOpacity>
                    ))}
                </ScrollView>

                {/* Categories */}
                <View style={styles.sectionHeader}>
                    <Text style={styles.sectionTitle}>What are you looking for?</Text>
                </View>
                <ScrollView
                    horizontal
                    showsHorizontalScrollIndicator={false}
                    contentContainerStyle={styles.categories}
                >
                    {categories.map(cat => (
                        <TouchableOpacity
                            key={cat.id}
                            style={[
                                styles.categoryCard,
                                selectedCategory?.id === cat.id && styles.selectedCategory
                            ]}
                            onPress={() => setSelectedCategory(cat.id === selectedCategory?.id ? null : cat)}
                        >
                            <BlurView intensity={selectedCategory?.id === cat.id ? 80 : 30} tint="light" style={[
                                styles.categoryIcon,
                                selectedCategory?.id === cat.id && { backgroundColor: 'rgba(226, 55, 68, 0.8)' }
                            ]}>
                                <Ionicons
                                    name={cat.icon}
                                    size={24}
                                    color={selectedCategory?.id === cat.id ? COLORS.white : COLORS.text}
                                />
                            </BlurView>
                            <Text style={[
                                styles.categoryLabel,
                                selectedCategory?.id === cat.id && { color: COLORS.white }
                            ]}>{cat.label}</Text>
                        </TouchableOpacity>
                    ))}
                </ScrollView>

                {/* Nearby Salons */}
                <View style={styles.sectionHeader}>
                    <Text style={styles.sectionTitle}>Recommended for You</Text>
                    <TouchableOpacity>
                        <Text style={styles.seeAll}>See All</Text>
                    </TouchableOpacity>
                </View>

                {nearestCityFallback && (
                    <View style={styles.fallbackNotice}>
                        <Ionicons name="information-circle" size={18} color="#666" />
                        <Text style={styles.fallbackText}>
                            Showing results from {nearestCityFallback.city.name} ({nearestCityFallback.distKm}km away)
                        </Text>
                    </View>
                )}

                <View style={styles.salonGrid}>
                    {filteredSalons.map(salon => (
                        <TouchableOpacity
                            key={salon.id}
                            style={styles.salonCardContainer}
                            onPress={() => handleSelectSalon(salon)}
                        >
                            <BlurView intensity={50} tint="light" style={styles.salonCard}>
                                <Image source={{ uri: salon.image_url || salon.img }} style={styles.salonImg} />
                                <View style={styles.ratingBadge}>
                                    <Ionicons name="star" size={12} color="#FFD700" />
                                    <Text style={styles.ratingText}>{salon.rating}</Text>
                                </View>
                                <View style={styles.salonInfo}>
                                    <Text style={styles.salonName} numberOfLines={1}>{salon.name}</Text>
                                    <Text style={styles.salonAddress} numberOfLines={1}>{salon.address}</Text>
                                    <View style={styles.priceRow}>
                                        <Text style={styles.priceText}>Starting from ₹199</Text>
                                        <View style={styles.openTag}>
                                            <Text style={styles.openText}>Open</Text>
                                        </View>
                                    </View>
                                </View>
                            </BlurView>
                        </TouchableOpacity>
                    ))}
                </View>

                <View style={{ height: 100 }} />
            </ScrollView>
        </LinearGradient>
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
        paddingHorizontal: 20,
        paddingTop: 50,
        paddingBottom: 20,
        backgroundColor: 'transparent',
    },
    locationContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        flex: 1,
    },
    cityName: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    areaName: {
        fontSize: 12,
        color: COLORS.textSecondary,
        width: 200,
    },
    notificationBtn: {
        width: 44,
        height: 44,
        borderRadius: 22,
        backgroundColor: '#F3F4F6',
        justifyContent: 'center',
        alignItems: 'center',
    },
    dot: {
        position: 'absolute',
        top: 12,
        right: 12,
        width: 8,
        height: 8,
        borderRadius: 4,
        backgroundColor: COLORS.primary,
        borderWidth: 2,
        borderColor: COLORS.white,
    },
    searchSection: {
        padding: 20,
    },
    searchBar: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.white,
        paddingHorizontal: 15,
        height: 50,
        borderRadius: 12,
        ...SHADOW,
    },
    searchInput: {
        flex: 1,
        marginLeft: 10,
        fontSize: 16,
        color: COLORS.text,
    },
    banners: {
        paddingLeft: 20,
        paddingBottom: 20,
    },
    bannerCard: {
        width: 280,
        height: 140,
        borderRadius: 20,
        marginRight: 15,
        padding: 20,
        flexDirection: 'row',
        justifyContent: 'space-between',
        overflow: 'hidden',
    },
    bannerTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#111',
    },
    bannerSubtitle: {
        fontSize: 12,
        color: '#444',
        marginTop: 4,
    },
    bannerBtn: {
        backgroundColor: '#000',
        paddingHorizontal: 15,
        paddingVertical: 8,
        borderRadius: 8,
        marginTop: 15,
        alignSelf: 'flex-start',
    },
    bannerBtnText: {
        color: COLORS.white,
        fontSize: 12,
        fontWeight: 'bold',
    },
    bannerImg: {
        width: 80,
        height: 80,
        position: 'absolute',
        right: 10,
        bottom: 10,
        opacity: 0.8,
    },
    sectionHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: 20,
        marginBottom: 15,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    seeAll: {
        color: COLORS.primary,
        fontWeight: '600',
    },
    categories: {
        paddingLeft: 20,
        paddingBottom: 20,
    },
    categoryCard: {
        alignItems: 'center',
        marginRight: 20,
        width: 70,
    },
    selectedCategory: {
        backgroundColor: COLORS.primary,
        padding: 10,
        borderRadius: 15,
        width: 80,
    },
    categoryIcon: {
        width: 54,
        height: 54,
        borderRadius: 27,
        backgroundColor: 'rgba(255, 255, 255, 0.4)',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 8,
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.6)',
        overflow: 'hidden',
    },
    categoryLabel: {
        fontSize: 12,
        fontWeight: '600',
        color: COLORS.text,
        textAlign: 'center',
    },
    salonGrid: {
        paddingHorizontal: 20,
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
    },
    salonCardContainer: {
        width: '48%',
        marginBottom: 20,
        borderRadius: 15,
        overflow: 'hidden',
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.6)',
        ...SHADOW,
    },
    salonCard: {
        width: '100%',
        backgroundColor: 'rgba(255, 255, 255, 0.3)',
    },
    salonImg: {
        width: '100%',
        height: 120,
    },
    ratingBadge: {
        position: 'absolute',
        top: 10,
        right: 10,
        backgroundColor: 'rgba(0,0,0,0.6)',
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 6,
        paddingVertical: 3,
        borderRadius: 8,
    },
    ratingText: {
        color: COLORS.white,
        fontSize: 10,
        fontWeight: 'bold',
        marginLeft: 3,
    },
    salonInfo: {
        padding: 12,
    },
    salonName: {
        fontSize: 15,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    salonAddress: {
        fontSize: 11,
        color: COLORS.textSecondary,
        marginTop: 2,
    },
    priceRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: 8,
    },
    priceText: {
        fontSize: 11,
        fontWeight: '700',
        color: COLORS.primary,
    },
    openTag: {
        backgroundColor: '#E8F5E9',
        paddingHorizontal: 6,
        paddingVertical: 2,
        borderRadius: 4,
    },
    openText: {
        fontSize: 9,
        color: '#2E7D32',
        fontWeight: 'bold',
    },
    fallbackNotice: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#F3F4F6',
        marginHorizontal: 20,
        padding: 10,
        borderRadius: 8,
        marginBottom: 15,
    },
    fallbackText: {
        fontSize: 12,
        color: '#666',
        marginLeft: 8,
    },
});
