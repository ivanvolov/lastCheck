import { redirect } from "next/navigation";

export default function Home() {
  redirect("/setup/step1-connect");
}
