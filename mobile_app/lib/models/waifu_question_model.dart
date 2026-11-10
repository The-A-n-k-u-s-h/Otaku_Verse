int _asInt(dynamic value) {
  if (value is int) return value;
  return int.tryParse(value?.toString() ?? '') ?? 0;
}

String _asString(dynamic value) => value == null ? '' : value.toString();

class WaifuMedia {
  final String imageUrl;
  final String gifUrl;
  final String audioUrl;

  const WaifuMedia({
    this.imageUrl = '',
    this.gifUrl = '',
    this.audioUrl = '',
  });

  factory WaifuMedia.fromJson(dynamic value, {Map<String, dynamic>? fallback}) {
    final map = value is Map
        ? Map<String, dynamic>.from(value)
        : <String, dynamic>{};
    final source = fallback ?? const <String, dynamic>{};
    return WaifuMedia(
      imageUrl: _asString(map['image_url'] ?? source['image_url']),
      gifUrl: _asString(map['gif_url'] ?? source['gif_url']),
      audioUrl: _asString(map['audio_url'] ?? source['audio_url']),
    );
  }

  String get visualUrl => gifUrl.isNotEmpty ? gifUrl : imageUrl;
}

class WaifuAnswerOption {
  final int id;
  final String text;
  final WaifuMedia media;

  const WaifuAnswerOption({
    required this.id,
    required this.text,
    this.media = const WaifuMedia(),
  });

  factory WaifuAnswerOption.fromJson(Map<String, dynamic> json) {
    return WaifuAnswerOption(
      id: _asInt(json['id']),
      text: _asString(json['text'] ?? json['option_text']),
      media: WaifuMedia.fromJson(json['media'], fallback: json),
    );
  }
}

class WaifuQuestion {
  final int id;
  final String prompt;
  final String category;
  final String profileType;
  final List<WaifuAnswerOption> options;
  final WaifuMedia media;
  final String difficulty;

  const WaifuQuestion({
    required this.id,
    required this.prompt,
    required this.category,
    required this.profileType,
    required this.options,
    this.media = const WaifuMedia(),
    this.difficulty = '',
  });

  factory WaifuQuestion.fromJson(Map<String, dynamic> json) {
    final rawOptions = json['options'];
    final options = rawOptions is List
        ? rawOptions
            .whereType<Map>()
            .map((item) => WaifuAnswerOption.fromJson(
                  Map<String, dynamic>.from(item),
                ))
            .toList()
        : <WaifuAnswerOption>[];

    return WaifuQuestion(
      id: _asInt(json['id']),
      prompt: _asString(json['prompt'] ?? json['question_text']),
      category: _asString(json['category']),
      profileType: _asString(json['profile_type']),
      options: options,
      media: WaifuMedia.fromJson(json['media'], fallback: json),
      difficulty: _asString(json['difficulty']),
    );
  }
}

class WaifuProgress {
  final int answered;
  final int availableQuestions;
  final int personalityAnswers;
  final int romanticAnswers;
  final bool completed;

  const WaifuProgress({
    required this.answered,
    required this.availableQuestions,
    required this.personalityAnswers,
    required this.romanticAnswers,
    required this.completed,
  });

  factory WaifuProgress.fromJson(dynamic value) {
    final json = value is Map
        ? Map<String, dynamic>.from(value)
        : <String, dynamic>{};
    int number(String key) {
      final raw = json[key];
      if (raw is int) return raw;
      return int.tryParse(raw?.toString() ?? '') ?? 0;
    }
    return WaifuProgress(
      answered: number('answered'),
      availableQuestions: number('available_questions'),
      personalityAnswers: number('personality_answers'),
      romanticAnswers: number('romantic_answers'),
      completed: json['completed'] == true,
    );
  }

  double get fraction => availableQuestions <= 0
      ? 0
      : (answered / availableQuestions).clamp(0.0, 1.0).toDouble();
}
