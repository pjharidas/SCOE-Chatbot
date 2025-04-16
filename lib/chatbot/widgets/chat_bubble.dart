import 'package:flutter/material.dart';

class ChatBubble extends StatelessWidget {
  final bool isBot;
  final String message;
  final Function? onRegenerate;
  final Function? onEdit;
  const ChatBubble({super.key, required this.isBot, required this.message, this.onRegenerate, this.onEdit});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: isBot ? CrossAxisAlignment.start : CrossAxisAlignment.end,
      children: [
        Align(
          alignment: isBot ? Alignment.centerLeft : Alignment.centerRight,
          child: Container(
            padding: const EdgeInsets.only(left: 20,right:20, top: 10), // Increased vertical padding
            margin: const EdgeInsets.symmetric(vertical: 5, horizontal: 5), // Adjusted vertical margin
            decoration: BoxDecoration(
              color: isBot ? Colors.blue : Colors.green,
              boxShadow: [
                BoxShadow(
                  color: isBot ? Colors.blue.withOpacity(0.8) : Colors.green.withOpacity(0.8),
                  blurRadius: 4,
                  offset: const Offset(2, 2), // Adjust the offset as needed
                ),
              ],
              borderRadius: BorderRadius.only(
                topLeft: isBot ? Radius.circular(0) : Radius.circular(20),
                topRight: Radius.circular(20),
                bottomLeft: Radius.circular(20),
                bottomRight: isBot ? Radius.circular(20) : Radius.circular(0),
              ),
            ),
            child: SelectableText.rich(
              (() {
              TextSpan parseMessage(String message) {
                List<TextSpan> spans = [];
                final defaultStyle = const TextStyle(
                  color: Colors.white, fontSize: 16, fontWeight: FontWeight.w500);
                final headingStyle = defaultStyle.copyWith( 
                  fontSize: 20, fontWeight: FontWeight.bold);
        
                for (var line in message.split('\n')) {
                if (line.startsWith('---') && line.endsWith('---')) {
                  // Heading text between --- and ---
                  final content = line.substring(3, line.length - 3).trim();
                  spans.add(TextSpan(text: content, style: headingStyle,));
                  spans.add(const TextSpan(text: "\n"));
                } else if (line.startsWith('- ')) {
                  // List item starting with '- '
                  final content = line.substring(2).trim();
                  spans.add(TextSpan(text: '    • $content', style: defaultStyle));
                  spans.add(const TextSpan(text: "\n"));
                } else {
                  int currentIndex = 0;
                  final regex = RegExp(r'\*(.*?)\*');
                  for (final match in regex.allMatches(line)) {
                  if (match.start > currentIndex) {
                    spans.add(TextSpan(
                      text: line.substring(currentIndex, match.start),
                      style: defaultStyle));
                  }
                  spans.add(TextSpan(
                    text: match.group(1),
                    style: defaultStyle.copyWith(fontWeight: FontWeight.bold)));
                  currentIndex = match.end;
                  }
                  if (currentIndex < line.length) {
                  spans.add(TextSpan(
                    text: line.substring(currentIndex), style: defaultStyle));
                  }
                  // Add newline after processing the full line
                  spans.add(const TextSpan(text: "\n"));
                }
                }
                return TextSpan(children: spans, style: defaultStyle);
              }
              return parseMessage(message);
              })(),),
          ),
        ),
        if (!isBot) // Only show buttons below user messages
          Padding(
            padding: const EdgeInsets.only(right: 10.0, top: 2.0), // Add padding for alignment
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                IconButton(
                  icon:  Icon(Icons.refresh, size: 18, color: Colors.grey[700]),
                  onPressed: () {
                    // TODO: Implement regenerate action
                    onRegenerate?.call(); // Call the edit function if provided
                    print('Regenerate tapped');
                  },
                  tooltip: 'Regenerate',
                  visualDensity: VisualDensity.compact, // Make icon button smaller
                  padding: EdgeInsets.zero, // Remove default padding
                  constraints: const BoxConstraints(), // Remove default constraints
                ),
                const SizedBox(width: 8), // Spacing between icons
                IconButton(
                  icon:  Icon(Icons.edit, size: 18, color: Colors.blueGrey[700]),
                  onPressed: () {
                    // TODO: Implement edit action
                    onEdit?.call(); // Call the regenerate function if provided
                    print('Edit tapped');
                  },
                  tooltip: 'Edit',
                  visualDensity: VisualDensity.compact,
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                ),
              ],
            ),
          ),
      ],
    );
  }
}
