export function UserMessage({ text }: { text: string }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[80%] px-4 py-2 rounded-2xl bg-blue-600">{text}</div>
    </div>
  );
}
