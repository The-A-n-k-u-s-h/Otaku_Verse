import '../models/waifu_result_model.dart';
import 'api_service.dart';

class WaifuResultService {
  WaifuResultService._();
  static final WaifuResultService instance = WaifuResultService._();

  Future<WaifuMatchResult> fetchResult() async {
    final response = await ApiService.instance.getJson('/api/waifu/result/');
    if (response['success'] != true || response['result'] is! Map) {
      throw Exception(response['message']?.toString() ??
          'The backend did not return a Waifu match.');
    }
    return WaifuMatchResult.fromJson(
      Map<String, dynamic>.from(response['result'] as Map),
    );
  }
}
