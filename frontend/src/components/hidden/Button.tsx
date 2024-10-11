import Alert from "./Alert";

interface Props {
  children: string;
  color?: "primary"|"secondary"|"success"|"danger"|"warning"|"info"|"light"|"dark";
  onClick: () => void;
}

const Button = ({children, color = 'warning', onClick}: Props) => {

const GetColor = (color: string) => {
  return `btn btn-${color}`
};

  return (
    <button type="button" className={GetColor(color)} onClick={onClick}>
      {children}
    </button>
  );
};

export default Button;
