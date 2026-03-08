import React, { useState, useEffect } from 'react';
import { View, StyleSheet, StatusBar, TouchableOpacity, Text, SafeAreaView, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SHADOW } from './src/constants/theme';
import { API_BASE_URL } from './src/constants/api';
import { LinearGradient } from 'expo-linear-gradient';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Screens
import HomeScreen from './src/screens/HomeScreen';
import SalonDetail from './src/screens/SalonDetail';
import BookingSummary from './src/screens/BookingSummary';
import BookingsScreen from './src/screens/BookingsScreen';

// Mock Data (to match frontend logic)
const categories = [
  { id: 'c1', label: 'Haircut', icon: 'cut' },
  { id: 'c2', label: 'Beard', icon: 'male' },
  { id: 'c3', label: 'Facial', icon: 'happy-outline' },
  { id: 'c4', label: 'Spa', icon: 'leaf-outline' },
  { id: 'c5', label: 'Bridal', icon: 'heart-outline' },
  { id: 'c7', label: 'Tattoos', icon: 'brush-outline' },
];

const banners = [
  { id: 'b1', title: 'Flat 30% OFF', subtitle: 'On all haircuts', color: '#FFE6E9' },
  { id: 'b2', title: 'Free Beard Trim', subtitle: 'With facial booking', color: '#FFF4E6' },
];

// (Workers are now fetched live from the backend when a salon is selected)

const slots = ['10:00 AM', '11:00 AM', '12:00 PM', '02:00 PM', '03:00 PM', '04:00 PM'];

export default function App() {
  const [tab, setTab] = useState('home');
  const [screen, setScreen] = useState('splash');
  const [isReady, setIsReady] = useState(false);

  // App State
  const [salons, setSalons] = useState([]);
  const [selectedSalon, setSelectedSalon] = useState(null);
  const [selectedServices, setSelectedServices] = useState([]);
  const [selectedWorker, setSelectedWorker] = useState(null);
  const [salonWorkers, setSalonWorkers] = useState([]);  // Real workers from API
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [selectedDate, setSelectedDate] = useState('Today');
  const [favorites, setFavorites] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(null);

  useEffect(() => {
    // Simulate App Loading & checking persisted login state
    const loadApp = async () => {
      try {
        await fetchSalons();
        // Here you would normally check AsyncStorage for auth token
        // e.g., const token = await AsyncStorage.getItem('userToken');
        setTimeout(() => {
          setScreen('home');
          setIsReady(true);
        }, 2500); // 2.5 second splash display
      } catch (e) {
        console.warn(e);
      }
    };

    loadApp();
  }, []);

  const fetchSalons = async () => {
    try {
      const resp = await fetch(`${API_BASE_URL}/user/salons`);
      const data = await resp.json();
      setSalons(data);
    } catch (err) {
      console.log("Fetch error:", err);
    }
  };

  const handleSelectSalon = async (salon) => {
    setSelectedSalon(salon);
    setSelectedServices([]);
    setSelectedWorker(null);
    setSelectedSlot(null);
    setScreen('salon');
    // Fetch real workers for this salon from backend
    try {
      const resp = await fetch(`${API_BASE_URL}/user/salon/${salon.id}/workers`);
      const data = await resp.json();
      if (Array.isArray(data) && data.length > 0) {
        setSalonWorkers(data);
      } else {
        // Fallback placeholder if salon has no workers yet
        setSalonWorkers([{ id: 0, name: 'Any Available', skill: 'Expert', image_url: 'https://i.pravatar.cc/300?img=8' }]);
      }
    } catch (err) {
      console.log('Error fetching workers:', err);
      setSalonWorkers([{ id: 0, name: 'Any Available', skill: 'Expert', image_url: 'https://i.pravatar.cc/300?img=8' }]);
    }
  };

  const confirmBooking = async () => {
    try {
      const resp = await fetch(`${API_BASE_URL}/user/booking/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 1,
          worker_id: selectedWorker?.id || 1,
          salon_id: selectedSalon.id,
          service_id: selectedServices[0].id,
          slot_time: `2026-03-05 ${selectedSlot.replace(' AM', ':00').replace(' PM', ':00')}`
        })
      });
      const data = await resp.json();
      if (data.status === 'success') {
        setTab('bookings');
        setScreen('home');
      }
    } catch (err) {
      console.log(err);
    }
  };

  const salonTotal = selectedServices.reduce((sum, s) => sum + s.price, 0);

  const renderContent = () => {
    if (screen === 'splash') {
      return (
        <LinearGradient
          colors={['#f09433', '#e6683c', '#dc2743', '#cc2366', '#bc1888']}
          style={styles.splashContainer}
          start={{ x: 0.0, y: 0.0 }}
          end={{ x: 1.0, y: 1.0 }}
        >
          <View style={styles.splashLogoContainer}>
            <Ionicons name="cut" size={60} color={COLORS.white} />
          </View>
          <Text style={styles.splashTitle}>SALOON ESSY</Text>
          <Text style={styles.splashTagline}>Book Top Salons Near You</Text>
          <View style={{ position: 'absolute', bottom: 100 }}>
            <ActivityIndicator size="large" color={COLORS.white} />
          </View>
        </LinearGradient>
      );
    }

    if (screen === 'salon') {
      return (
        <SalonDetail
          selectedSalon={selectedSalon}
          setScreen={setScreen}
          markFavorite={(id) => setFavorites(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])}
          favorites={favorites}
          toggleService={(s) => setSelectedServices(prev => prev.find(x => x.id === s.id) ? prev.filter(x => x.id !== s.id) : [...prev, s])}
          selectedServices={selectedServices}
          workers={salonWorkers}
          selectedWorker={selectedWorker}
          setSelectedWorker={setSelectedWorker}
          slots={slots}
          selectedSlot={selectedSlot}
          setSelectedSlot={setSelectedSlot}
          selectedDate={selectedDate}
          setSelectedDate={setSelectedDate}
          salonTotal={salonTotal}
        />
      );
    }

    if (screen === 'summary') {
      return (
        <BookingSummary
          selectedSalon={selectedSalon}
          selectedServices={selectedServices}
          selectedWorker={selectedWorker}
          selectedSlot={selectedSlot}
          salonTotal={salonTotal}
          confirmBooking={confirmBooking}
        />
      );
    }

    switch (tab) {
      case 'home':
        return (
          <HomeScreen
            currentArea="HITEC City, Hyderabad"
            currentCity={{ name: 'Hyderabad' }}
            setShowLocationPicker={() => { }}
            banners={banners}
            categories={categories}
            filteredSalons={salons}
            handleSelectSalon={handleSelectSalon}
            selectedCategory={selectedCategory}
            setSelectedCategory={setSelectedCategory}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
          />
        );
      case 'bookings':
        return <BookingsScreen setScreen={setScreen} />;
      case 'profile':
        return (
          <View style={styles.center}>
            <Text>Profile Screen Coming Soon</Text>
            <TouchableOpacity style={styles.logoutBtn} onPress={() => setTab('home')}>
              <Text style={{ color: COLORS.white }}>Back to Home</Text>
            </TouchableOpacity>
          </View>
        );
      default:
        return <HomeScreen />;
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" />
      {renderContent()}

      {/* Navigation Bar */}
      {isReady && screen === 'home' && (
        <View style={styles.tabBar}>
          <TabItem icon="home" label="Home" active={tab === 'home'} onPress={() => setTab('home')} />
          <TabItem icon="calendar" label="Bookings" active={tab === 'bookings'} onPress={() => setTab('bookings')} />
          <TabItem icon="person" label="Profile" active={tab === 'profile'} onPress={() => setTab('profile')} />
        </View>
      )}
    </View>
  );
}

function TabItem({ icon, label, active, onPress }) {
  return (
    <TouchableOpacity style={styles.tabItem} onPress={onPress}>
      <Ionicons name={active ? icon : `${icon}-outline`} size={24} color={active ? COLORS.primary : COLORS.textSecondary} />
      <Text style={[styles.tabLabel, { color: active ? COLORS.primary : COLORS.textSecondary }]}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.white,
  },
  tabBar: {
    flexDirection: 'row',
    height: 80,
    backgroundColor: COLORS.white,
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
    paddingBottom: 20,
    justifyContent: 'space-around',
    alignItems: 'center',
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    ...SHADOW,
  },
  tabItem: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabLabel: {
    fontSize: 11,
    fontWeight: '600',
    marginTop: 4,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoutBtn: {
    marginTop: 20,
    padding: 15,
    backgroundColor: COLORS.primary,
    borderRadius: 10,
  },
  splashContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  splashLogoContainer: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  splashTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFF',
    letterSpacing: 2,
  },
  splashTagline: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.9)',
    marginTop: 8,
  }
});
