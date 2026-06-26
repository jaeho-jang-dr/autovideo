import React, { useEffect, useState } from "react";
import { Button, Rows, Text, Columns, Box } from "@canva/app-ui-kit";
import { upload } from "@canva/asset";
import { addElementAtCursor, addElementAtPoint } from "@canva/design";
import { useFeatureSupport } from "@canva/app-hooks";
import * as styles from "styles/components.css";

interface CharacterAsset {
  id: number;
  name_kr: string;
  name_en: string;
  type: string;
  file_path: string;
  url: string;
  flow_prompt: string;
}

export const App = () => {
  const isSupported = useFeatureSupport();
  const addElement = [addElementAtPoint, addElementAtCursor].find((fn) =>
    isSupported(fn)
  );

  const [characters, setCharacters] = useState<CharacterAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState<"character" | "letter" | "object">("character");

  // 로컬 개발 서버 및 프로덕션 서버 fallback 처리
  const BASE_URLS = [
    "http://localhost:4321",
    "https://drjayed.vercel.app"
  ];

  useEffect(() => {
    const fetchAssets = async () => {
      let lastErr: any = null;
      for (const base of BASE_URLS) {
        try {
          const res = await fetch(`${base}/api/character-assets`);
          if (res.ok) {
            const data = await res.json();
            // 각 캐릭터의 url 필드에 도메인 접두사 바인딩
            const mapped = data.characters.map((ch: CharacterAsset) => ({
              ...ch,
              url: ch.url.startsWith("http") ? ch.url : `${base}${ch.url}`
            }));
            setCharacters(mapped);
            setLoading(false);
            return;
          }
        } catch (err) {
          lastErr = err;
        }
      }
      setError(lastErr ? String(lastErr) : "Failed to fetch assets");
      setLoading(false);
    };

    fetchAssets();
  }, []);

  const handleAddImage = async (char: CharacterAsset) => {
    if (!addElement) {
      alert("Element insertion not supported in the current view.");
      return;
    }

    try {
      // Canva SDK 업로드 개시
      const image = await upload({
        type: "image",
        mimeType: "image/png",
        url: char.url,
        thumbnailUrl: char.url,
        width: 512,
        height: 512,
        aiDisclosure: "none",
      });

      // 캔버스 중앙/커서 위치에 삽입
      await addElement({
        type: "image",
        ref: image.ref,
        altText: {
          text: char.name_en,
          decorative: undefined,
        },
      });

      await image.whenUploaded();
      console.log(`Successfully imported ${char.name_en} to Canva!`);
    } catch (err) {
      console.error("Canva asset upload failed:", err);
      alert(`Upload failed: ${String(err)}`);
    }
  };

  const filteredCharacters = characters.filter((char) => {
    const query = searchQuery.toLowerCase();
    const matchesSearch = char.name_kr.toLowerCase().includes(query) ||
      char.name_en.toLowerCase().includes(query);
    const matchesTab = char.type === activeTab;
    return matchesSearch && matchesTab;
  });

  return (
    <div className={styles.scrollContainer} style={{ padding: "12px", height: "100%" }}>
      <Rows spacing="2u">
        <Box padding="1u" background="contrast" borderRadius="large">
          <Text align="center" weight="bold">
            🎨 Stickman (Zolla) Importer
          </Text>
        </Box>

        {/* Tab Buttons */}
        <div style={{ display: "flex", gap: "4px" }}>
          {(["character", "letter", "object"] as const).map((tab) => {
            const label = tab === "character" ? "Characters" : tab === "letter" ? "Letters" : "Objects";
            const on = activeTab === tab;
            return (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  flex: 1,
                  padding: "6px 4px",
                  fontSize: "12px",
                  fontWeight: "bold",
                  borderRadius: "4px",
                  border: "1px solid rgba(0,0,0,0.1)",
                  background: on ? "#b5852a" : "#fff",
                  color: on ? "#fff" : "#1c1813",
                  cursor: "pointer",
                  transition: "all 0.15s ease"
                }}
              >
                {label}
              </button>
            );
          })}
        </div>

        <input
          type="text"
          placeholder="Search characters (e.g. Jieun, Pointing)..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            width: "100%",
            padding: "8px",
            borderRadius: "6px",
            border: "1px solid rgba(0,0,0,0.15)",
            fontSize: "14px"
          }}
        />

        {loading && <Text align="center">Loading character database...</Text>}
        {error && (
          <Text align="center" tone="critical">
            Error: {error}
          </Text>
        )}

        {!loading && !error && (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "8px",
              maxHeight: "70vh",
              overflowY: "auto",
              paddingBottom: "20px"
            }}
          >
            {filteredCharacters.map((char) => (
              <div
                key={char.id}
                onClick={() => handleAddImage(char)}
                style={{
                  border: "1px solid rgba(0,0,0,0.08)",
                  borderRadius: "8px",
                  padding: "6px",
                  cursor: "pointer",
                  textAlign: "center",
                  background: "rgba(255, 255, 255, 0.6)",
                  boxShadow: "0 2px 6px rgba(0,0,0,0.03)",
                  transition: "transform 0.2s, box-shadow 0.2s"
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-2px)";
                  e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.08)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "none";
                  e.currentTarget.style.boxShadow = "0 2px 6px rgba(0,0,0,0.03)";
                }}
              >
                <img
                  src={char.url}
                  alt={char.name_en}
                  style={{
                    width: "80px",
                    height: "80px",
                    objectFit: "contain",
                    background: "#F5F5F0", // 베이스 배경과 매칭
                    borderRadius: "6px",
                    marginBottom: "4px"
                  }}
                  onError={(e) => {
                    // 이미지 로드 실패 시 투명 플레이스홀더 처리
                    e.currentTarget.src = "/logo.png";
                  }}
                />
                <div style={{ fontSize: "11px", fontWeight: "bold", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                  {char.name_kr}
                </div>
                <div style={{ fontSize: "9px", color: "#666", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                  {char.name_en}
                </div>
              </div>
            ))}
          </div>
        )}
      </Rows>
    </div>
  );
};
