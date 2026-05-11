import React from 'react';
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';

const LANDSCAPE_W = 146;
const LANDSCAPE_H = 83;
const PORTRAIT_W = 100;
const PORTRAIT_H = 150;

export default function ContentCard({ show, cardType = 'landscape', onPress }) {
  const isPortrait = cardType === 'portrait';
  const cardW = isPortrait ? PORTRAIT_W : LANDSCAPE_W;
  const cardH = isPortrait ? PORTRAIT_H : LANDSCAPE_H;

  return (
    <TouchableOpacity style={[styles.container, { width: cardW }]} onPress={() => onPress(show)} activeOpacity={0.85}>
      <View style={[styles.imageWrapper, { width: cardW, height: cardH }]}>
        <Image
          source={{ uri: show.thumbnail }}
          style={styles.image}
          resizeMode="cover"
        />
        {/* Progress bar overlay at bottom of thumbnail */}
        <View style={styles.progressOverlay}>
          <View style={styles.progressTrack}>
            <View style={[styles.progressFill, { width: `${show.progress * 100}%` }]} />
          </View>
        </View>
      </View>

      {/* Title + episode below image */}
      <View style={styles.infoRow}>
        <Text style={styles.title} numberOfLines={1}>{show.title}</Text>
        {show.season && show.episode ? (
          <Text style={styles.episode}>S{show.season} - E{show.episode}</Text>
        ) : null}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    marginRight: 6,
  },
  imageWrapper: {
    borderRadius: 6,
    overflow: 'hidden',
    backgroundColor: '#1a1a2e',
  },
  image: {
    width: '100%',
    height: '100%',
    position: 'absolute',
  },
  progressOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 18,
    justifyContent: 'flex-end',
    paddingBottom: 4,
    paddingHorizontal: 12,
    backgroundColor: 'transparent',
  },
  progressTrack: {
    height: 3,
    borderRadius: 2,
    backgroundColor: 'rgba(255,255,255,0.3)',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 2,
    backgroundColor: '#fff',
  },
  infoRow: {
    paddingTop: 4,
    paddingHorizontal: 3,
  },
  title: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '500',
    color: '#fff',
  },
  episode: {
    fontFamily: 'System',
    fontSize: 10,
    color: 'rgba(255,255,255,0.7)',
    marginTop: 1,
  },
});
