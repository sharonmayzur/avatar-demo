import React, { useState, useRef, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TouchableWithoutFeedback,
  StatusBar,
  Dimensions,
  Image,
  Animated,
} from 'react-native';
import { Video, ResizeMode } from 'expo-av';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const { width: SCREEN_W, height: SCREEN_H } = Dimensions.get('window');

export default function PlayerScreen({ navigation, route }) {
  const { show } = route.params;
  const insets = useSafeAreaInsets();
  const videoRef = useRef(null);

  const [overlayVisible, setOverlayVisible] = useState(true);
  const [isPlaying, setIsPlaying] = useState(true);
  const [progress, setProgress] = useState(show.progress || 0);
  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(show.likes);

  const overlayOpacity = useRef(new Animated.Value(1)).current;

  const toggleOverlay = useCallback(() => {
    const toValue = overlayVisible ? 0 : 1;
    Animated.timing(overlayOpacity, {
      toValue,
      duration: 200,
      useNativeDriver: true,
    }).start();
    setOverlayVisible(!overlayVisible);
  }, [overlayVisible, overlayOpacity]);

  const handlePlaybackStatusUpdate = (status) => {
    if (status.isLoaded && status.durationMillis) {
      setProgress(status.positionMillis / status.durationMillis);
      setIsPlaying(status.isPlaying);
    }
  };

  const togglePlayPause = async () => {
    if (videoRef.current) {
      if (isPlaying) {
        await videoRef.current.pauseAsync();
      } else {
        await videoRef.current.playAsync();
      }
    }
    setIsPlaying(!isPlaying);
  };

  const handleLike = () => {
    setLiked(!liked);
    setLikeCount((c) => (liked ? c - 1 : c + 1));
  };

  const goBack = () => {
    navigation.goBack();
  };

  return (
    <View style={styles.container}>
      <StatusBar hidden />

      {/* Video fills the screen */}
      <Video
        ref={videoRef}
        source={{ uri: show.videoUrl }}
        style={styles.video}
        resizeMode={ResizeMode.COVER}
        shouldPlay
        isLooping
        onPlaybackStatusUpdate={handlePlaybackStatusUpdate}
      />

      {/* Full-screen tap area to toggle overlay */}
      <TouchableWithoutFeedback onPress={toggleOverlay}>
        <View style={StyleSheet.absoluteFill} />
      </TouchableWithoutFeedback>

      {/* ── OVERLAY ELEMENTS ── */}
      <View style={StyleSheet.absoluteFill} pointerEvents="box-none">

        {/* TOP BAR: back button + episode badge */}
        <Animated.View
          style={[styles.topBar, { paddingTop: insets.top + 8, opacity: overlayOpacity }]}
          pointerEvents={overlayVisible ? 'box-none' : 'none'}
        >
          <TouchableOpacity style={styles.backBtn} onPress={goBack} hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}>
            <Ionicons name="arrow-back" size={22} color="#fff" />
          </TouchableOpacity>
          <View style={styles.episodeBadge}>
            <Ionicons name="play-circle" size={13} color="rgba(255,255,255,0.8)" />
            <Text style={styles.episodeBadgeText}>
              S{show.season} EP{show.episode}
            </Text>
          </View>
        </Animated.View>

        {/* RIGHT SIDE: social action buttons */}
        <Animated.View
          style={[styles.rightActions, { opacity: overlayOpacity }]}
          pointerEvents={overlayVisible ? 'box-none' : 'none'}
        >
          {/* Coins / gift icon */}
          <TouchableOpacity style={styles.actionItem}>
            <View style={styles.coinIcon}>
              <Text style={styles.coinEmoji}>🪙</Text>
            </View>
          </TouchableOpacity>

          {/* Like */}
          <TouchableOpacity style={styles.actionItem} onPress={handleLike}>
            <Ionicons
              name={liked ? 'heart' : 'heart-outline'}
              size={30}
              color={liked ? '#ff4d6d' : '#fff'}
            />
            <Text style={styles.actionCount}>{likeCount}</Text>
          </TouchableOpacity>

          {/* Comment */}
          <TouchableOpacity style={styles.actionItem}>
            <Ionicons name="chatbubble-outline" size={28} color="#fff" />
            <Text style={styles.actionCount}>{show.comments}</Text>
          </TouchableOpacity>

          {/* Share */}
          <TouchableOpacity style={styles.actionItem}>
            <Ionicons name="arrow-redo-outline" size={28} color="#fff" />
            <Text style={styles.actionCount}>Share</Text>
          </TouchableOpacity>

          {/* More */}
          <TouchableOpacity style={styles.actionItem}>
            <Ionicons name="ellipsis-horizontal-circle-outline" size={28} color="#fff" />
            <Text style={styles.actionCount}>More</Text>
          </TouchableOpacity>
        </Animated.View>

        {/* BOTTOM AREA */}
        <View
          style={[styles.bottomArea, { paddingBottom: insets.bottom + 12 }]}
          pointerEvents="box-none"
        >
          {/* Title, genre, play button — hidden when overlay off */}
          <Animated.View style={{ opacity: overlayOpacity }} pointerEvents={overlayVisible ? 'box-none' : 'none'}>
            {/* Thumbnail + title row */}
            <View style={styles.titleRow}>
              <Image
                source={{ uri: show.thumbnail }}
                style={styles.miniThumb}
              />
              <View style={styles.titleInfo}>
                <Text style={styles.showTitle}>{show.title}</Text>
                <Text style={styles.showGenre}>{show.genre}</Text>
              </View>
              <TouchableOpacity style={styles.playPauseBtn} onPress={togglePlayPause}>
                <Ionicons
                  name={isPlaying ? 'pause' : 'play'}
                  size={20}
                  color="#fff"
                />
              </TouchableOpacity>
            </View>
          </Animated.View>

          {/* Progress bar — ALWAYS VISIBLE */}
          <View style={styles.progressContainer} pointerEvents="none">
            <View style={styles.progressTrack}>
              <View style={[styles.progressFill, { width: `${progress * 100}%` }]} />
            </View>
          </View>

          {/* Episode info below progress bar — ALWAYS VISIBLE */}
          <View style={styles.episodeInfoRow} pointerEvents="none">
            <Ionicons name="play" size={10} color="rgba(255,255,255,0.6)" />
            <Text style={styles.episodeInfo}>
              Season {show.season}, Episode {show.episode}
            </Text>
            <Text style={styles.episodeTitle}>{show.episodeTitle}</Text>
          </View>
        </View>

      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  video: {
    width: SCREEN_W,
    height: SCREEN_H,
    position: 'absolute',
    top: 0,
    left: 0,
  },
  // TOP BAR
  topBar: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    backgroundColor: 'rgba(0,0,0,0.35)',
    paddingBottom: 12,
  },
  backBtn: {
    width: 36,
    height: 36,
    alignItems: 'center',
    justifyContent: 'center',
  },
  episodeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: 'rgba(0,0,0,0.4)',
    borderRadius: 12,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  episodeBadgeText: {
    color: 'rgba(255,255,255,0.9)',
    fontSize: 11,
    fontWeight: '600',
  },

  // RIGHT ACTIONS
  rightActions: {
    position: 'absolute',
    right: 12,
    bottom: 200,
    alignItems: 'center',
    gap: 4,
  },
  actionItem: {
    alignItems: 'center',
    marginBottom: 16,
  },
  actionCount: {
    color: '#fff',
    fontSize: 11,
    marginTop: 3,
    textShadowColor: 'rgba(0,0,0,0.8)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 3,
  },
  coinIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(255,200,0,0.2)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  coinEmoji: {
    fontSize: 22,
  },

  // BOTTOM
  bottomArea: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    paddingHorizontal: 15,
    backgroundColor: 'rgba(0,0,0,0.4)',
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingTop: 14,
    paddingBottom: 10,
  },
  miniThumb: {
    width: 38,
    height: 38,
    borderRadius: 4,
    backgroundColor: '#222',
  },
  titleInfo: {
    flex: 1,
  },
  showTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '700',
  },
  showGenre: {
    color: 'rgba(255,255,255,0.7)',
    fontSize: 11,
    marginTop: 2,
  },
  playPauseBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: 'rgba(255,255,255,0.15)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  progressContainer: {
    marginBottom: 8,
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
  episodeInfoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingBottom: 4,
  },
  episodeInfo: {
    color: 'rgba(255,255,255,0.6)',
    fontSize: 10,
  },
  episodeTitle: {
    color: 'rgba(255,255,255,0.9)',
    fontSize: 10,
    fontWeight: '600',
  },
});
