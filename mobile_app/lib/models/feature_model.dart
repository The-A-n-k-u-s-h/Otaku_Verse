import 'package:flutter/material.dart';

class FeatureModel {
  final String title;
  final String shortTitle;
  final String description;
  final String image;
  final String audio;
  final String buttonText;
  final String route;
  final IconData icon;
  final Color accent;

  const FeatureModel({
    required this.title,
    required this.shortTitle,
    required this.description,
    required this.image,
    required this.audio,
    required this.buttonText,
    required this.route,
    required this.icon,
    required this.accent,
  });
}

const List<FeatureModel> otakuFeatures = [
  FeatureModel(
    title: 'Anime Recommendations',
    shortTitle: 'Anime',
    description:
        'Discover your next favourite series through genres, moods and interests.',
    image: 'assets/images/recommendations.png',
    audio: 'audio/recommendations.mp3',
    buttonText: 'Explore recommendations',
    route: '/recommendations',
    icon: Icons.auto_awesome_rounded,
    accent: Color(0xFF9B70E8),
  ),
  FeatureModel(
    title: 'Anime Quiz',
    shortTitle: 'Quiz',
    description:
        'Challenge your anime knowledge with character, story and trivia questions.',
    image: 'assets/images/quiz.png',
    audio: 'audio/quiz.mp3',
    buttonText: 'Play quiz',
    route: '/quiz',
    icon: Icons.quiz_rounded,
    accent: Color(0xFF35B8A1),
  ),
  FeatureModel(
    title: 'Character Match',
    shortTitle: 'Match',
    description:
        'Answer personality questions and discover the anime character who matches you.',
    image: 'assets/images/character_match.png',
    audio: 'audio/character_match.mp3',
    buttonText: 'Find your match',
    route: '/character-match',
    icon: Icons.favorite_rounded,
    accent: Color(0xFFE875A5),
  ),
  FeatureModel(
    title: 'Anime Hot Takes',
    shortTitle: 'Hot Takes',
    description:
        'Explore bold opinions, vote on debates and share your own anime takes.',
    image: 'assets/images/hot_takes.png',
    audio: 'audio/hot_takes.mp3',
    buttonText: 'Explore hot takes',
    route: '/hot-takes',
    icon: Icons.local_fire_department_rounded,
    accent: Color(0xFFFF985C),
  ),
  FeatureModel(
    title: 'Anime Discussions',
    shortTitle: 'Discuss',
    description:
        'Meet other fans and talk about the anime, characters and stories you love.',
    image: 'assets/images/discussions.png',
    audio: 'audio/discussions.mp3',
    buttonText: 'Join discussions',
    route: '/discussions',
    icon: Icons.forum_rounded,
    accent: Color(0xFF63A6F5),
  ),
];
