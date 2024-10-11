import { Fragment } from "react/jsx-runtime";
import { MouseEvent, useState } from "react";

interface Props {
  items: string[];
  heading: string;

  onSelectItem: (item: string) => void;
}

function ListGroup({ items, heading, onSelectItem }: Props) {
  // let selectedIndex = -1;

  // Hook
  const [selectedIndex, setSelectedIndex] = useState(-1);

  // const message = items.length === 0 ? <p>No item found.</p> : null;
  const message2 = items.length === 0 && <p>No item found.</p>;
  const GetMessage = () => {
    return message2;
  };

  // Event handler
  const handleClick =
    (item: string, index: number) => (event: React.MouseEvent) => {
      console.log(event, `Clicked ${item} ${selectedIndex}`);
      setSelectedIndex(index);
      onSelectItem(item);
    };

  return (
    <Fragment>
      <h1>{heading}</h1>
      {GetMessage()}
      <ul className="list-group">
        {items.map((item, index) => (
          <li
            className={
              selectedIndex === index
                ? "list-group-item active"
                : "list-group-item"
            }
            key={item}
            onClick={handleClick(item, index)}
          >
            {item}
          </li>
        ))}
      </ul>
    </Fragment>
  );
}

export default ListGroup;
