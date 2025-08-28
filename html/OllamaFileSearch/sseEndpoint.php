<?php
// SSEヘッダー
header('Content-Type: text/event-stream');
header('Cache-Control: no-cache');
header('Connection: keep-alive');
header('Access-Control-Allow-Origin: *');

// タイムアウト防止
set_time_limit(0);
// PHPの出力バッファを無効化
while (ob_get_level() > 0) {
    ob_end_flush();
}
ob_implicit_flush(true);

$baseDir = "/usr/local/lib/OllamaFileSearch";
$pythonPath = $baseDir . "/py/.venv/Scripts/python.exe";


# --- 実行 (SSEストリーム開始) ---
echo "retry: 1000\n\n";	# 再接続までの待機ミリ秒
flush();

// POSTデータ取得
$prompt = escapeshellarg(rawurldecode($_GET['prompt'] ?? ''));
// Chroma検索を実行
$searchResults = shell_exec("{$pythonPath} -u {$baseDir}/py/searchEndpoint.py " . $prompt);

// 検索結果をSSEで送信
echo "event: search\n";
echo "data: " . ($searchResults ?: "[]") . "\n\n";
flush();

// LLM回答を生成
$cmd = "{$pythonPath} -u {$baseDir}/py/genAnswerEndpoint.py " . $prompt;
$process = popen($cmd, 'r');

if($process) {
	while (!feof($process)) {
		$line = fgets($process);
		$tline = trim($line);
		if ($line !== false && $tline !== '') {
			// トークンを逐次送信
			echo "event: answer_token\n";
			echo "data: " . rtrim($line) . "\n\n";
			flush();
		}
	}
	pclose($process);
}

// 終了を通知
echo "event: end\n";
echo "data: {}\n\n";
flush();
?>