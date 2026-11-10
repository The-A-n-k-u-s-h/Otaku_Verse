class WaifuHistoryItem {
  final int id;
  final String matchId;
  final int characterId;
  final String characterName;
  final String animeTitle;
  final String imageUrl;
  final double overallScore;
  final double personalityScore;
  final double romanticScore;
  final String createdAt;

  const WaifuHistoryItem({
    required this.id,
    required this.matchId,
    required this.characterId,
    required this.characterName,
    required this.animeTitle,
    required this.imageUrl,
    required this.overallScore,
    required this.personalityScore,
    required this.romanticScore,
    required this.createdAt,
  });

  factory WaifuHistoryItem.fromJson(Map<String, dynamic> json) {
    double number(dynamic value) =>
        value is num ? value.toDouble() : double.tryParse('$value') ?? 0;

    return WaifuHistoryItem(
      id: (json['id'] as num?)?.toInt() ?? int.tryParse('${json['id']}') ?? 0,
      matchId: '${json['match_id'] ?? ''}',
      characterId: (json['character_id'] as num?)?.toInt() ??
          int.tryParse('${json['character_id']}') ?? 0,
      characterName: '${json['character_name'] ?? 'Unknown character'}',
      animeTitle: '${json['anime_title'] ?? 'Unknown anime'}',
      imageUrl: '${json['image_url'] ?? ''}',
      overallScore: number(json['overall_score']),
      personalityScore: number(json['personality_score']),
      romanticScore: number(json['romantic_score']),
      createdAt: '${json['created_at'] ?? ''}',
    );
  }
}

class WaifuHistoryDetail {
  final WaifuHistoryItem item;
  final Map<String, dynamic> snapshot;
  final Map<String, dynamic> explanation;

  const WaifuHistoryDetail({
    required this.item,
    required this.snapshot,
    required this.explanation,
  });

  factory WaifuHistoryDetail.fromJson(Map<String, dynamic> json) {
    final snapshot = json['snapshot'] is Map
        ? Map<String, dynamic>.from(json['snapshot'])
        : <String, dynamic>{};
    final explanation = json['explanation'] is Map
        ? Map<String, dynamic>.from(json['explanation'])
        : <String, dynamic>{};
    final character = snapshot['character'] is Map
        ? Map<String, dynamic>.from(snapshot['character'])
        : <String, dynamic>{};
    final compatibility = snapshot['compatibility'] is Map
        ? Map<String, dynamic>.from(snapshot['compatibility'])
        : <String, dynamic>{};

    final base = <String, dynamic>{
      'id': json['id'],
      'match_id': json['match_id'],
      'character_id': json['character_id'] ?? character['id'],
      'character_name': json['character_name'] ?? character['name'],
      'anime_title': json['anime_title'] ?? character['anime_title'],
      'image_url': json['image_url'] ?? character['image_url'],
      'overall_score': json['overall_score'] ?? compatibility['overall_score'],
      'personality_score':
          json['personality_score'] ?? compatibility['personality_score'],
      'romantic_score':
          json['romantic_score'] ?? compatibility['romantic_score'],
      'created_at': json['created_at'],
    };

    return WaifuHistoryDetail(
      item: WaifuHistoryItem.fromJson(base),
      snapshot: snapshot,
      explanation: explanation,
    );
  }
}
