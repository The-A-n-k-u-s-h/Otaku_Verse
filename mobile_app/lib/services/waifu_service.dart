import '../models/waifu_question_model.dart';
import 'api_service.dart';

class WaifuStartResponse {
  final String matchId;
  final WaifuQuestion? question;
  final WaifuProgress progress;

  const WaifuStartResponse({
    required this.matchId,
    required this.question,
    required this.progress,
  });
}

class WaifuAnswerResponse {
  final WaifuQuestion? nextQuestion;
  final WaifuProgress progress;
  final bool completed;

  const WaifuAnswerResponse({
    required this.nextQuestion,
    required this.progress,
    required this.completed,
  });
}

class WaifuService {
  WaifuService._();
  static final WaifuService instance = WaifuService._();
  final ApiService _api = ApiService.instance;

  Future<WaifuStartResponse> startQuestionnaire() async {
    final json = await _api.postJson('/api/waifu/profile/start', {});
    final rawQuestion = json['question'];
    return WaifuStartResponse(
      matchId: (json['match_id'] ?? '').toString(),
      question: rawQuestion is Map
          ? WaifuQuestion.fromJson(Map<String, dynamic>.from(rawQuestion))
          : null,
      progress: WaifuProgress.fromJson(json['progress']),
    );
  }

  Future<WaifuQuestion?> getNextQuestion() async {
    final json = await _api.getJson('/api/waifu/profile/next');
    final rawQuestion = json['question'];
    if (rawQuestion is! Map) return null;
    return WaifuQuestion.fromJson(Map<String, dynamic>.from(rawQuestion));
  }

  Future<WaifuAnswerResponse> submitAnswer({
    required int questionId,
    required int optionId,
  }) async {
    final json = await _api.postJson('/api/waifu/profile/answer', {
      'question_id': questionId,
      'option_id': optionId,
    });
    final rawQuestion = json['next_question'];
    return WaifuAnswerResponse(
      nextQuestion: rawQuestion is Map
          ? WaifuQuestion.fromJson(Map<String, dynamic>.from(rawQuestion))
          : null,
      progress: WaifuProgress.fromJson(json['progress']),
      completed: json['completed'] == true || rawQuestion == null,
    );
  }

  Future<Map<String, dynamic>> getProfiles() =>
      _api.getJson('/api/waifu/profile/profiles');
}
