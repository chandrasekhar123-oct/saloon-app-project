import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, ScrollView, SafeAreaView, TouchableOpacity, Image, Modal, FlatList, Alert } from 'react-native';
import { COLORS, SPACING, SIZES } from '../constants/theme';
import { Button } from '../components/Button';
import { Camera, ChevronDown } from 'lucide-react-native';
import * as ImagePicker from 'expo-image-picker';
import { API_BASE_URL } from '../constants/api';

const SKILLS = ['Haircut', 'Beard Trim', 'Facial', 'Hair Color', 'Head Massage', 'Shaving'];

export default function RegisterScreen({ navigation }) {
    const [selectedSkills, setSelectedSkills] = useState([]);
    const [salon, setSalon] = useState(null);
    const [salonsList, setSalonsList] = useState([]);
    const [showSalonModal, setShowSalonModal] = useState(false);
    const [name, setName] = useState('');
    const [phone, setPhone] = useState('');
    const [experience, setExperience] = useState('');
    const [password, setPassword] = useState('');
    const [image, setImage] = useState(null);
    const [loading, setLoading] = useState(false);

    React.useEffect(() => {
        fetchSalons();
    }, []);

    const fetchSalons = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/worker/salons`);
            const data = await response.json();
            setSalonsList(data);
        } catch (error) {
            console.error("Fetch salons error:", error);
        }
    };

    const handleRegister = async () => {
        if (!name || !phone || !salon || !password) {
            Alert.alert("Error", "Please fill all required fields");
            return;
        }

        setLoading(true);
        try {
            const formData = new FormData();
            formData.append('name', name);
            formData.append('phone', phone);
            formData.append('password', password);
            formData.append('salon_id', salon.id.toString());
            formData.append('experience', experience || '0');
            formData.append('skill', selectedSkills.join(', '));

            if (image) {
                const filename = image.split('/').pop();
                const match = /\.(\w+)$/.exec(filename);
                const type = match ? `image/${match[1]}` : `image`;
                formData.append('photo', { uri: image, name: filename, type });
            }

            const response = await fetch(`${API_BASE_URL}/worker/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'multipart/form-data' },
                body: formData
            });
            const data = await response.json();

            if (data.status === 'success') {
                Alert.alert("Welcome! 🎉", "Registration successful! You can login now.", [
                    { text: "Login", onPress: () => navigation.replace('Login') }
                ]);
            } else if (data.status === 'pending') {
                Alert.alert("Pending Approval", data.message);
            } else {
                Alert.alert("Registration Failed", data.message);
            }
        } catch (error) {
            Alert.alert("Error", "Could not complete registration");
        } finally {
            setLoading(false);
        }
    };

    const pickImage = async () => {
        // No permissions request is necessary for launching the image library
        let result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ['images'],
            allowsEditing: true,
            aspect: [1, 1],
            quality: 1,
        });

        if (!result.canceled) {
            setImage(result.assets[0].uri);
        }
    };

    const toggleSkill = (skill) => {
        if (selectedSkills.includes(skill)) {
            setSelectedSkills(selectedSkills.filter(s => s !== skill));
        } else {
            setSelectedSkills([...selectedSkills, skill]);
        }
    };

    return (
        <SafeAreaView style={styles.container}>
            <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
                <Text style={styles.title}>Create Account</Text>
                <Text style={styles.subtitle}>Join our network of professional barbers</Text>

                <TouchableOpacity style={styles.photoContainer} onPress={pickImage}>
                    <View style={styles.photoPlaceholder}>
                        {image ? (
                            <Image source={{ uri: image }} style={styles.selectedImage} />
                        ) : (
                            <View style={{ alignItems: 'center' }}>
                                <Camera size={30} color={COLORS.textSecondary} />
                                <Text style={styles.photoText}>Upload Profile Photo</Text>
                            </View>
                        )}
                    </View>
                </TouchableOpacity>

                <View style={styles.form}>
                    <View style={styles.inputContainer}>
                        <Text style={styles.label}>Full Name</Text>
                        <TextInput
                            style={styles.input}
                            placeholder="Enter your name"
                            value={name}
                            onChangeText={setName}
                        />
                    </View>

                    <View style={styles.inputContainer}>
                        <Text style={styles.label}>Phone Number</Text>
                        <TextInput
                            style={styles.input}
                            placeholder="Enter phone number"
                            keyboardType="phone-pad"
                            value={phone}
                            onChangeText={setPhone}
                        />
                    </View>

                    <View style={styles.inputContainer}>
                        <Text style={styles.label}>Password</Text>
                        <TextInput
                            style={styles.input}
                            placeholder="Create password"
                            secureTextEntry
                            value={password}
                            onChangeText={setPassword}
                        />
                    </View>

                    <View style={styles.inputContainer}>
                        <Text style={styles.label}>Experience (Years)</Text>
                        <TextInput
                            style={styles.input}
                            placeholder="e.g. 5"
                            keyboardType="numeric"
                            value={experience}
                            onChangeText={setExperience}
                        />
                    </View>

                    <View style={styles.inputContainer}>
                        <Text style={styles.label}>Skills (Select all that apply)</Text>
                        <View style={styles.skillsGrid}>
                            {SKILLS.map(skill => (
                                <TouchableOpacity
                                    key={skill}
                                    style={[
                                        styles.skillChip,
                                        selectedSkills.includes(skill) && styles.skillChipActive
                                    ]}
                                    onPress={() => toggleSkill(skill)}
                                >
                                    <Text style={[
                                        styles.skillText,
                                        selectedSkills.includes(skill) && styles.skillTextActive
                                    ]}>{skill}</Text>
                                </TouchableOpacity>
                            ))}
                        </View>
                    </View>

                    <View style={styles.inputContainer}>
                        <Text style={styles.label}>Select Working Salon</Text>
                        <TouchableOpacity style={styles.dropdown} onPress={() => setShowSalonModal(true)}>
                            <Text style={styles.dropdownText}>{salon ? salon.name : 'Choose a salon'}</Text>
                            <ChevronDown size={20} color={COLORS.textSecondary} />
                        </TouchableOpacity>
                    </View>

                    <Button
                        title={loading ? "Registering..." : "Submit Join Request"}
                        style={styles.submitButton}
                        onPress={handleRegister}
                        disabled={loading}
                    />

                    <TouchableOpacity onPress={() => navigation.navigate('Login')} style={styles.backLink}>
                        <Text style={styles.backLinkText}>Already have an account? Login</Text>
                    </TouchableOpacity>
                </View>

                {/* Salon Selection Modal */}
                <Modal visible={showSalonModal} animationType="slide" transparent={true}>
                    <View style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' }}>
                        <View style={{ backgroundColor: COLORS.white, borderTopLeftRadius: 30, borderTopRightRadius: 30, padding: 20, maxHeight: '70%' }}>
                            <Text style={[styles.title, { fontSize: 20, marginBottom: 15 }]}>Select Your Salon</Text>
                            <FlatList
                                data={salonsList}
                                keyExtractor={(item) => item.id.toString()}
                                renderItem={({ item }) => (
                                    <TouchableOpacity
                                        style={{ padding: 15, borderBottomWidth: 1, borderBottomColor: COLORS.border }}
                                        onPress={() => { setSalon(item); setShowSalonModal(false); }}
                                    >
                                        <Text style={{ fontSize: 16, color: COLORS.text, fontWeight: '600' }}>{item.name}</Text>
                                        <Text style={{ fontSize: 13, color: COLORS.textSecondary }}>{item.location}</Text>
                                    </TouchableOpacity>
                                )}
                            />
                            <Button title="Close" variant="secondary" onPress={() => setShowSalonModal(false)} style={{ marginTop: 10 }} />
                        </View>
                    </View>
                </Modal>
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    scrollContent: {
        padding: SPACING.xl,
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    subtitle: {
        fontSize: 16,
        color: COLORS.textSecondary,
        marginBottom: SPACING.xl,
    },
    photoContainer: {
        alignItems: 'center',
        marginBottom: SPACING.xl,
    },
    photoPlaceholder: {
        width: 120,
        height: 120,
        borderRadius: 60,
        backgroundColor: COLORS.surface,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 1,
        borderStyle: 'dashed',
        borderColor: COLORS.border,
        overflow: 'hidden', // Add this
    },
    selectedImage: {
        width: '100%',
        height: '100%',
    },
    photoText: {
        fontSize: 12,
        color: COLORS.textSecondary,
        marginTop: SPACING.xs,
        textAlign: 'center',
        paddingHorizontal: SPACING.sm,
    },
    form: {
        marginTop: SPACING.md,
    },
    inputContainer: {
        marginBottom: SPACING.lg,
    },
    label: {
        fontSize: 14,
        fontWeight: '600',
        color: COLORS.text,
        marginBottom: SPACING.sm,
    },
    input: {
        backgroundColor: COLORS.surface,
        height: SIZES.buttonHeight,
        borderRadius: SIZES.radius,
        paddingHorizontal: SPACING.md,
        fontSize: 16,
        color: COLORS.text,
    },
    skillsGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        marginHorizontal: -SPACING.xs,
    },
    skillChip: {
        backgroundColor: COLORS.surface,
        paddingHorizontal: SPACING.md,
        paddingVertical: SPACING.sm,
        borderRadius: 20,
        margin: SPACING.xs,
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    skillChipActive: {
        backgroundColor: COLORS.primary,
        borderColor: COLORS.primary,
    },
    skillText: {
        color: COLORS.text,
        fontSize: 14,
    },
    skillTextActive: {
        color: COLORS.white,
        fontWeight: '600',
    },
    dropdown: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: COLORS.surface,
        height: SIZES.buttonHeight,
        borderRadius: SIZES.radius,
        paddingHorizontal: SPACING.md,
    },
    dropdownText: {
        fontSize: 16,
        color: COLORS.text,
    },
    submitButton: {
        marginTop: SPACING.xl,
        marginBottom: SPACING.md,
    },
    backLink: {
        alignItems: 'center',
        marginVertical: SPACING.md,
    },
    backLinkText: {
        color: COLORS.textSecondary,
        fontSize: 16,
    },
});
