import { Card as AntCard, Typography } from "antd";
import type { Card } from "../../../api/types";
import "./ItemCards.css";

// Short values only: long text and lists belong to the details, not a card
const MAX_VALUE_LENGTH = 30;
const MAX_DETAILS = 4;

// "review_count" → "Review count"
function humanize(code: string): string {
  const words = code.replace(/_/g, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

// The card's attributes worth a line: numbers and short text, not its name again
function details(card: Card): [string, string][] {
  return Object.entries(card.attributes)
    .filter(([, value]) =>
      typeof value === "number" ||
      (typeof value === "string" && value !== card.label && value.length <= MAX_VALUE_LENGTH),
    )
    .slice(0, MAX_DETAILS)
    .map(([code, value]) => [humanize(code), String(value)]);
}

// The results a reply shows, in order: "the second one" is the second card
export function ItemCards({ cards }: { cards: Card[] }) {
  return (
    <div className="item-cards">
      {cards.map((card) => (
        <AntCard key={card.reference} size="small" className="item-card">
          <Typography.Paragraph className="item-card__label" ellipsis={{ rows: 2, tooltip: card.label }}>
            {card.label}
          </Typography.Paragraph>
          {details(card).map(([name, value]) => (
            <div key={name} className="item-card__detail">
              <span>{name}</span>
              <span>{value}</span>
            </div>
          ))}
        </AntCard>
      ))}
    </div>
  );
}
