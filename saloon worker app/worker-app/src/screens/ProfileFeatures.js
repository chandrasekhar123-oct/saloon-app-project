import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TextInput, TouchableOpacity, Switch, Modal, Alert, Image } from 'react-native';
import { COLORS, SPACING, SIZES } from '../constants/theme';
import { Button } from '../components/Button';
import { ChevronLeft, Save, Plus, Trash2, Camera, MapPin } from 'lucide-react-native';
import { API_BASE_URL } from '../constants/api';
import * as ImagePicker from 'expo-image-picker';

const Header = ({ title, navigation }) => (
    <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
            <ChevronLeft size={24} color={COLORS.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{title}</Text>
        <View style={{ width: 40 }} />
    </View>
);

export const EditProfileScreen = ({ route, navigation }) => {
    const workerId = route?.params?.workerId || 1;
    const [name, setName] = useState('');
    const [phone, setPhone] = useState('');
    const [skill, setSkill] = useState('');
    const [imageUrl, setImageUrl] = useState('');
    const [salonId, setSalonId] = useState(null);
    const [salonName, setSalonName] = useState('');

    const [saloons, setSaloons] = useState([]);
    const [modalVisible, setModalVisible] = useState(false);

    useEffect(() => {
        const fetchWorkerAndSaloons = async () => {
            try {
                // Fetch Worker Info
                const workerRes = await fetch(`${API_BASE_URL}/worker/${workerId}`);
                const workerData = await workerRes.json();
                if (workerData.status !== 'error') {
                    setName(workerData.name || '');
                    setPhone(workerData.phone || '');
                    setSkill(workerData.skill || '');
                    setImageUrl(workerData.image_url || '');
                    setSalonId(workerData.salon_id);
                    setSalonName(workerData.salon_name);
                }

                // Fetch Saloons
                const salonRes = await fetch(`${API_BASE_URL}/worker/salons`);
                const salonData = await salonRes.json();
                setSaloons(salonData || []);
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };
        fetchWorkerAndSaloons();
    }, [workerId]);

    const pickImage = async () => {
        let result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ['images'],
            allowsEditing: true,
            aspect: [1, 1],
            quality: 0.5,
        });

        if (!result.canceled) {
            const uri = result.assets[0].uri;
            setImageUrl(uri); // temporary preview

            let formData = new FormData();
            formData.append('photo', {
                uri: uri,
                name: 'photo.jpg',
                type: 'image/jpeg'
            });

            try {
                const response = await fetch(`${API_BASE_URL}/worker/${workerId}/upload-photo`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
                const data = await response.json();
                if (data.status === 'success') {
                    setImageUrl(data.image_url);
                    Alert.alert('Success', 'Profile photo uploaded!');
                } else {
                    Alert.alert('Upload failed', data.message || 'Could not upload');
                }
            } catch (e) {
                console.log(e);
                Alert.alert('Error', 'Could not upload photo');
            }
        }
    };

    const handleSave = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/worker/${workerId}/update`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name,
                    phone,
                    skill,
                    image_url: imageUrl,
                    salon_id: salonId
                })
            });
            const data = await response.json();
            if (response.ok) {
                Alert.alert("Success", "Profile updated. If you changed shop, please wait for new owner approval.");
                navigation.goBack();
            } else {
                Alert.alert("Error", data.message || "Update failed");
            }
        } catch (error) {
            Alert.alert("Error", "Could not connect to server");
        }
    };

    return (
        <SafeAreaView style={styles.container}>
            <Header title="Edit Profile" navigation={navigation} />
            <ScrollView contentContainerStyle={styles.scrollContent}>

                <View style={[styles.section, { alignItems: 'center' }]}>
                    <TouchableOpacity onPress={pickImage} style={styles.imagePickerContainer}>
                        {imageUrl ? (
                            <Image source={{ uri: imageUrl }} style={styles.profileImageAvatar} />
                        ) : (
                            <View style={styles.placeholderImage}>
                                <Camera size={32} color={COLORS.textSecondary} />
                                <Text style={styles.placeholderText}>Add Photo</Text>
                            </View>
                        )}
                        <View style={styles.editIconContainer}>
                            <Camera size={14} color="white" />
                        </View>
                    </TouchableOpacity>
                </View>

                <View style={styles.section}>
                    <Text style={styles.label}>Full Name</Text>
                    <TextInput style={styles.input} value={name} onChangeText={setName} />
                </View>
                <View style={styles.section}>
                    <Text style={styles.label}>Phone Number</Text>
                    <TextInput style={styles.input} value={phone} onChangeText={setPhone} keyboardType="phone-pad" />
                </View>
                <View style={styles.section}>
                    <Text style={styles.label}>Skills / Bio</Text>
                    <TextInput
                        style={[styles.input, { height: 100, textAlignVertical: 'top', paddingTop: 12 }]}
                        multiline
                        value={skill}
                        onChangeText={setSkill}
                    />
                </View>

                <View style={styles.section}>
                    <Text style={styles.label}>Assigned Saloon Shop</Text>
                    <TouchableOpacity style={styles.input} onPress={() => setModalVisible(true)}>
                        <Text style={{ lineHeight: 56, color: COLORS.text }}>{salonName || "Select Saloon Shop"}</Text>
                        <MapPin size={20} color={COLORS.primary} style={{ position: 'absolute', right: 16, top: 18 }} />
                    </TouchableOpacity>
                </View>

                <Button title="Save Changes" style={styles.saveButton} onPress={handleSave} />
            </ScrollView>

            <Modal visible={modalVisible} transparent={true} animationType="slide">
                <View style={styles.modalOverlay}>
                    <View style={styles.modalContent}>
                        <Text style={styles.modalTitle}>Change Saloon Shop</Text>
                        <ScrollView>
                            {saloons.map((salon) => (
                                <TouchableOpacity
                                    key={salon.id}
                                    style={styles.salonItem}
                                    onPress={() => {
                                        setSalonId(salon.id);
                                        setSalonName(salon.name);
                                        setModalVisible(false);
                                    }}
                                >
                                    <Text style={styles.salonItemName}>{salon.name}</Text>
                                    <Text style={styles.salonItemLocation}>{salon.location}</Text>
                                </TouchableOpacity>
                            ))}
                        </ScrollView>
                        <Button title="Cancel" variant="outline" onPress={() => setModalVisible(false)} style={{ marginTop: 10 }} />
                    </View>
                </View>
            </Modal>
        </SafeAreaView>
    );
};

export const MySkillsScreen = ({ navigation }) => {
    const [skills, setSkills] = useState(['Haircut', 'Beard Styling', 'Facial']);
    return (
        <SafeAreaView style={styles.container}>
            <Header title="My Skills" navigation={navigation} />
            <ScrollView contentContainerStyle={styles.scrollContent}>
                <View style={styles.skillsList}>
                    {skills.map((skill, index) => (
                        <View key={index} style={styles.skillItem}>
                            <Text style={styles.skillName}>{skill}</Text>
                            <TouchableOpacity onPress={() => setSkills(skills.filter((_, i) => i !== index))}>
                                <Trash2 size={20} color={COLORS.error} />
                            </TouchableOpacity>
                        </View>
                    ))}
                </View>
                <TouchableOpacity style={styles.addButton}>
                    <Plus size={20} color={COLORS.primary} />
                    <Text style={styles.addButtonText}>Add New Skill</Text>
                </TouchableOpacity>
            </ScrollView>
        </SafeAreaView>
    );
};

export const WorkHistoryScreen = ({ navigation }) => {
    const history = [
        { id: '1', customer: 'Rahul Sharma', service: 'Haircut', date: '02 March 2026', amount: '₹250' },
        { id: '2', customer: 'Amit Verma', service: 'Beard Trim', date: '01 March 2026', amount: '₹150' },
        { id: '3', customer: 'Suresh Kumar', service: 'Facial', date: '28 Feb 2026', amount: '₹500' },
    ];
    return (
        <SafeAreaView style={styles.container}>
            <Header title="Work History" navigation={navigation} />
            <ScrollView contentContainerStyle={styles.scrollContent}>
                {history.map(item => (
                    <View key={item.id} style={styles.historyCard}>
                        <View style={styles.historyInfo}>
                            <Text style={styles.customerName}>{item.customer}</Text>
                            <Text style={styles.serviceDate}>{item.service} • {item.date}</Text>
                        </View>
                        <Text style={styles.historyAmount}>{item.amount}</Text>
                    </View>
                ))}
            </ScrollView>
        </SafeAreaView>
    );
};

export const NotificationsScreen = ({ navigation }) => {
    const [bookingAlerts, setBookingAlerts] = useState(true);
    const [paymentAlerts, setPaymentAlerts] = useState(true);
    return (
        <SafeAreaView style={styles.container}>
            <Header title="Notifications" navigation={navigation} />
            <View style={styles.scrollContent}>
                <View style={styles.settingRow}>
                    <Text style={styles.settingLabel}>New Booking Requests</Text>
                    <Switch value={bookingAlerts} onValueChange={setBookingAlerts} trackColor={{ true: COLORS.primary }} />
                </View>
                <View style={styles.divider} />
                <View style={styles.settingRow}>
                    <Text style={styles.settingLabel}>Payment Success Alerts</Text>
                    <Switch value={paymentAlerts} onValueChange={setPaymentAlerts} trackColor={{ true: COLORS.primary }} />
                </View>
            </View>
        </SafeAreaView>
    );
};

export const BankDetailsScreen = ({ navigation }) => {
    return (
        <SafeAreaView style={styles.container}>
            <Header title="Bank Details" navigation={navigation} />
            <ScrollView contentContainerStyle={styles.scrollContent}>
                <View style={styles.section}>
                    <Text style={styles.label}>Account Holder Name</Text>
                    <TextInput style={styles.input} placeholder="Enter name as per bank" />
                </View>
                <View style={styles.section}>
                    <Text style={styles.label}>Account Number</Text>
                    <TextInput style={styles.input} placeholder="Enter account number" keyboardType="numeric" />
                </View>
                <View style={styles.section}>
                    <Text style={styles.label}>IFSC Code</Text>
                    <TextInput style={styles.input} placeholder="Enter IFSC code" autoCapitalize="characters" />
                </View>
                <Button title="Update Bank Details" style={styles.saveButton} onPress={() => navigation.goBack()} />
            </ScrollView>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingHorizontal: SPACING.md,
        paddingVertical: SPACING.md,
        borderBottomWidth: 1,
        borderBottomColor: COLORS.surface,
    },
    backButton: {
        padding: 8,
    },
    headerTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    scrollContent: {
        padding: SPACING.lg,
    },
    section: {
        marginBottom: SPACING.lg,
    },
    label: {
        fontSize: 14,
        fontWeight: '600',
        color: COLORS.textSecondary,
        marginBottom: 8,
    },
    input: {
        backgroundColor: COLORS.surface,
        height: 56,
        borderRadius: 12,
        paddingHorizontal: 16,
        fontSize: 16,
        color: COLORS.text,
    },
    saveButton: {
        marginTop: SPACING.xl,
    },
    skillsList: {
        marginBottom: SPACING.xl,
    },
    skillItem: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: 16,
        backgroundColor: COLORS.surface,
        borderRadius: 12,
        marginBottom: 12,
    },
    skillName: {
        fontSize: 16,
        fontWeight: '600',
        color: COLORS.text,
    },
    addButton: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 16,
        borderWidth: 1,
        borderColor: COLORS.primary,
        borderStyle: 'dashed',
        borderRadius: 12,
    },
    addButtonText: {
        marginLeft: 8,
        fontSize: 16,
        color: COLORS.primary,
        fontWeight: '600',
    },
    historyCard: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: 16,
        backgroundColor: COLORS.white,
        borderRadius: 12,
        marginBottom: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.05,
        shadowRadius: 5,
        elevation: 2,
    },
    customerName: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    serviceDate: {
        fontSize: 12,
        color: COLORS.textSecondary,
        marginTop: 4,
    },
    historyAmount: {
        fontSize: 16,
        fontWeight: 'bold',
        color: COLORS.primary,
    },
    settingRow: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingVertical: 20,
        paddingHorizontal: SPACING.lg,
    },
    settingLabel: {
        fontSize: 16,
        fontWeight: '600',
        color: COLORS.text,
    },
    divider: {
        height: 1,
        backgroundColor: COLORS.surface,
        marginHorizontal: SPACING.lg,
    },
    modalOverlay: {
        flex: 1,
        backgroundColor: 'rgba(0,0,0,0.5)',
        justifyContent: 'flex-end',
    },
    modalContent: {
        backgroundColor: COLORS.background,
        borderTopLeftRadius: 24,
        borderTopRightRadius: 24,
        padding: SPACING.lg,
        maxHeight: '80%',
    },
    modalTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: SPACING.md,
    },
    salonItem: {
        padding: SPACING.md,
        borderBottomWidth: 1,
        borderBottomColor: COLORS.surface,
    },
    salonItemName: {
        fontSize: 16,
        fontWeight: '600',
        color: COLORS.text,
    },
    salonItemLocation: {
        fontSize: 14,
        color: COLORS.textSecondary,
        marginTop: 4,
    },
    imagePickerContainer: {
        width: 120,
        height: 120,
        borderRadius: 60,
        borderWidth: 2,
        borderColor: COLORS.primary,
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: SPACING.xs,
    },
    profileImageAvatar: {
        width: 116,
        height: 116,
        borderRadius: 58,
    },
    placeholderImage: {
        alignItems: 'center',
        justifyContent: 'center',
    },
    placeholderText: {
        fontSize: 12,
        color: COLORS.textSecondary,
        marginTop: 4,
        fontWeight: '600'
    },
    editIconContainer: {
        position: 'absolute',
        bottom: 0,
        right: 0,
        width: 32,
        height: 32,
        borderRadius: 16,
        backgroundColor: COLORS.primary,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 3,
        borderColor: COLORS.background,
    },
});
