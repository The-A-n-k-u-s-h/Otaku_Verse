class WaifuMatchResult {
  final int characterId;
  final String characterName;
  final String animeTitle;
  final String imageUrl;
  final String description;
  final String biography;
  final double overallScore;
  final double personalityScore;
  final double romanticScore;
  final Map<String, dynamic> explanation;
  final String explanationSource;

  const WaifuMatchResult({
    required this.characterId,
    required this.characterName,
    required this.animeTitle,
    required this.imageUrl,
    required this.description,
    required this.biography,
    required this.overallScore,
    required this.personalityScore,
    required this.romanticScore,
    required this.explanation,
    required this.explanationSource,
  });

  factory WaifuMatchResult.fromJson(Map<String, dynamic> json) {
    final character = json['character'] is Map
        ? Map<String, dynamic>.from(json['character'] as Map)
        : <String, dynamic>{};
    final compatibility = json['compatibility'] is Map
        ? Map<String, dynamic>.from(json['compatibility'] as Map)
        : <String, dynamic>{};
    final explanation = json['explanation'] is Map
        ? Map<String, dynamic>.from(json['explanation'] as Map)
        : <String, dynamic>{};

    double number(dynamic value) {
      if (value is num) return value.toDouble();
      return double.tryParse(value?.toString() ?? '') ?? 0;
    }

    return WaifuMatchResult(
      characterId: int.tryParse('${character['id'] ?? 0}') ?? 0,
      characterName: '${character['name'] ?? 'Unknown character'}',
      animeTitle: '${character['anime_title'] ?? 'Unknown anime'}',
      imageUrl: '${character['image_url'] ?? ''}',
      description: '${character['description'] ?? ''}',
      biography: '${character['biography'] ?? ''}',
      overallScore: number(compatibility['overall']),
      personalityScore: number(compatibility['personality']),
      romanticScore: number(compatibility['romantic']),
      explanation: explanation,
      explanationSource: '${json['explanation_source'] ?? 'unknown'}',
    );
  }
}
