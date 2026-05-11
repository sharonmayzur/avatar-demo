import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  StatusBar,
  TouchableOpacity,
  SafeAreaView,
  Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import ContentRail from '../components/ContentRail';
import { SHOWS, RAILS } from '../data/mockData';

const FEATURED_SHOW = SHOWS[0];

export default function HomeScreen({ navigation }) {
  const getShowsForRail = (rail) =>
    rail.showIds.map((id) => SHOWS.find((s) => s.id === id)).filter(Boolean);

  const handleShowPress = (show) => {
    navigation.navigate('Player', { show });
  };

  return (
    <View style={styles.root}>
      <StatusBar barStyle="light-content" backgroundColor="#000" />

      {/* Top Bar */}
      <SafeAreaView style={styles.safeTop}>
        <View style={styles.topBar}>
          <Text style={styles.logo}>DRAMA</Text>
          <View style={styles.topActions}>
            <TouchableOpacity style={styles.iconBtn}>
              <Ionicons name="search-outline" size={22} color="#fff" />
            </TouchableOpacity>
            <TouchableOpacity style={styles.iconBtn}>
              <Ionicons name="notifications-outline" size={22} color="#fff" />
            </TouchableOpacity>
          </View>
        </View>
      </SafeAreaView>

      {/* Content */}
      <ScrollView
        style={styles.scroll}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {/* Featured / Hero banner */}
        <TouchableOpacity
          style={styles.hero}
          activeOpacity={0.9}
          onPress={() => handleShowPress(FEATURED_SHOW)}
        >
          <Image
            source={{ uri: FEATURED_SHOW.thumbnail }}
            style={styles.heroImage}
            resizeMode="cover"
          />
          <View style={styles.heroGradient} />
          <View style={styles.heroInfo}>
            <View style={styles.ratingBadge}>
              <Text style={styles.ratingText}>16+</Text>
            </View>
            <Text style={styles.heroTitle}>{FEATURED_SHOW.title}</Text>
            <Text style={styles.heroGenre}>{FEATURED_SHOW.genre}</Text>
            <TouchableOpacity
              style={styles.playButton}
              onPress={() => handleShowPress(FEATURED_SHOW)}
            >
              <Ionicons name="play" size={16} color="#000" />
              <Text style={styles.playButtonText}>Play Now</Text>
            </TouchableOpacity>
          </View>
        </TouchableOpacity>

        {/* Rails */}
        {RAILS.map((rail) => (
          <ContentRail
            key={rail.id}
            rail={rail}
            shows={getShowsForRail(rail)}
            onShowPress={handleShowPress}
          />
        ))}

        <View style={styles.bottomPad} />
      </ScrollView>

      {/* Bottom Navigation */}
      <View style={styles.bottomNav}>
        <TouchableOpacity style={styles.navItem}>
          <Ionicons name="home" size={22} color="#fff" />
          <Text style={styles.navLabelActive}>Home</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.navItem}>
          <Ionicons name="search-outline" size={22} color="rgba(255,255,255,0.5)" />
          <Text style={styles.navLabel}>Discover</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.navItem}>
          <Ionicons name="add-circle-outline" size={22} color="rgba(255,255,255,0.5)" />
          <Text style={styles.navLabel}>My List</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.navItem}>
          <Ionicons name="person-outline" size={22} color="rgba(255,255,255,0.5)" />
          <Text style={styles.navLabel}>Profile</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#000',
  },
  safeTop: {
    backgroundColor: '#000',
  },
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 15,
    paddingVertical: 10,
  },
  logo: {
    fontSize: 22,
    fontWeight: '900',
    color: '#fff',
    letterSpacing: 3,
  },
  topActions: {
    flexDirection: 'row',
    gap: 8,
  },
  iconBtn: {
    padding: 4,
  },
  scroll: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 20,
  },
  hero: {
    width: '100%',
    height: 260,
    marginBottom: 20,
    position: 'relative',
  },
  heroImage: {
    width: '100%',
    height: '100%',
  },
  heroGradient: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: '70%',
    backgroundColor: 'transparent',
    // fallback since LinearGradient needs expo-linear-gradient
    // Use a semi-transparent overlay
  },
  heroInfo: {
    position: 'absolute',
    bottom: 20,
    left: 15,
    right: 15,
  },
  ratingBadge: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.4)',
    borderRadius: 4,
    paddingHorizontal: 6,
    paddingVertical: 1,
    alignSelf: 'flex-start',
    marginBottom: 6,
  },
  ratingText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '600',
  },
  heroTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#fff',
    marginBottom: 4,
  },
  heroGenre: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.8)',
    marginBottom: 12,
  },
  playButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 6,
    paddingVertical: 8,
    paddingHorizontal: 16,
    alignSelf: 'flex-start',
    gap: 6,
  },
  playButtonText: {
    color: '#000',
    fontSize: 13,
    fontWeight: '700',
  },
  bottomPad: {
    height: 20,
  },
  bottomNav: {
    flexDirection: 'row',
    backgroundColor: '#111',
    borderTopWidth: 1,
    borderTopColor: '#222',
    paddingBottom: 20,
    paddingTop: 10,
  },
  navItem: {
    flex: 1,
    alignItems: 'center',
    gap: 3,
  },
  navLabel: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.5)',
  },
  navLabelActive: {
    fontSize: 10,
    color: '#fff',
    fontWeight: '600',
  },
});
