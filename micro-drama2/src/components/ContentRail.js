import React from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import ContentCard from './ContentCard';

export default function ContentRail({ rail, shows, onShowPress }) {
  return (
    <View style={styles.container}>
      <TouchableOpacity style={styles.header} activeOpacity={0.7}>
        <Text style={styles.title}>{rail.title}</Text>
        <Text style={styles.arrow}>{' >'}</Text>
      </TouchableOpacity>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {shows.map((show) => (
          <ContentCard
            key={show.id}
            show={show}
            cardType={rail.cardType}
            onPress={onShowPress}
          />
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 24,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 15,
    marginBottom: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: '700',
    color: '#fff',
  },
  arrow: {
    fontSize: 14,
    color: '#fff',
    marginLeft: 4,
  },
  scrollContent: {
    paddingHorizontal: 15,
  },
});
