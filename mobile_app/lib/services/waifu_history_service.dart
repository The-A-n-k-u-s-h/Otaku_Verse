import 'api_service.dart';
import '../models/waifu_history_model.dart';

class WaifuHistoryService {
  WaifuHistoryService._();
  static final WaifuHistoryService instance = WaifuHistoryService._();

  final ApiService _api = ApiService.instance;

  Future<List<WaifuHistoryItem>> getHistory({
    int limit = 50,
    int offset = 0,
  }) async {
    final result = await _api.getJson(
      '/api/waifu/history/?limit=$limit&offset=$offset',
    );
    final rows = result['history'];
    if (rows is! List) return [];
    return rows
        .whereType<Map>()
        .map((row) => WaifuHistoryItem.fromJson(
              Map<String, dynamic>.from(row),
            ))
        .toList();
  }

  Future<WaifuHistoryDetail> getDetail(int historyId) async {
    final result = await _api.getJson('/api/waifu/history/$historyId');
    final record = result['record'];
    if (record is! Map) {
      throw Exception('The backend did not return a history record.');
    }
    return WaifuHistoryDetail.fromJson(Map<String, dynamic>.from(record));
  }

  Future<void> deleteHistory(int historyId) async {
    await _api.deleteJson('/api/waifu/history/$historyId');
  }

  Future<int> clearHistory() async {
    final result = await _api.deleteJson('/api/waifu/history/');
    final count = result['deleted_count'];
    return count is num ? count.toInt() : 0;
  }
}
