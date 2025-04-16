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
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10), // Increased vertical padding
            margin: const EdgeInsets.symmetric(vertical: 5, horizontal: 5), // Adjusted vertical margin
            decoration: BoxDecoration(
              color: isBot ? Colors.blue : Colors.green,
              borderRadius: BorderRadius.only(
                topLeft: isBot ? Radius.circular(0) : Radius.circular(20),
                topRight: Radius.circular(20),
                bottomLeft: Radius.circular(20),
                bottomRight: isBot ? Radius.circular(20) : Radius.circular(0),
              ),
            ),
            child: SelectableText(message,
                style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w500)),
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
