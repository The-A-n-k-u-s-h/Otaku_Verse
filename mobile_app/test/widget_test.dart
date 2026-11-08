import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile_app/app.dart';

void main() {
  testWidgets('OtakuVerse home screen displays five feature destinations',
      (WidgetTester tester) async {
    await tester.pumpWidget(const OtakuVerseApp());
    await tester.pumpAndSettle();

    expect(find.text('Your Anime Universe'), findsOneWidget);
    expect(find.text('Continue as Guest'), findsOneWidget);
    expect(find.text('Anime'), findsWidgets);
    expect(find.text('Quiz'), findsOneWidget);
    expect(find.text('Match'), findsOneWidget);
    expect(find.text('Hot Takes'), findsOneWidget);
    expect(find.text('Discuss'), findsOneWidget);
  });
}
