// Top-level helper function accessible to all classes in this file
int _asInt(dynamic value) {
  if (value is int) return value;
  return int.tryParse(value?.toString() ?? '') ?? 0;
}

class WaifuAnswerOption {
  final int id;
  final String text;

  const WaifuAnswerOption({required this.id, required this.text});

  factory WaifuAnswerOption.fromJson(Map<String, dynamic> json) {
    return WaifuAnswerOption(
      id: _asInt(json['id']),
      text: (json['text'] ?? json['option_text'] ?? '').toString(),
    );
  }
}

class WaifuQuestion {
  final int id;
  final String prompt;
  final String category;
  final String profileType;
  final List<WaifuAnswerOption> options;

  const WaifuQuestion({
    required this.id,
    required this.prompt,
    required this.category,
    required this.profileType,
    required this.options,
  });

  factory WaifuQuestion.fromJson(Map<String, dynamic> json) {
    final rawOptions = json['options'];
    final options = rawOptions is List
        ? rawOptions
            .whereType()
            .map((item) => WaifuAnswerOption.fromJson(
                  Map<String, dynamic>.from(item),
                ))
            .toList()
        : <WaifuAnswerOption>[];

    return WaifuQuestion(
      id: _asInt(json['id']),
      prompt: (json['prompt'] ?? '').toString(),
      category: (json['category'] ?? '').toString(),
      profileType: (json['profile_type'] ?? '').toString(),
      options: options,
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

  double get fraction {
    if (availableQuestions <= 0) return 0;
    return (answered / availableQuestions).clamp(0.0, 1.0).toDouble();
  }
}