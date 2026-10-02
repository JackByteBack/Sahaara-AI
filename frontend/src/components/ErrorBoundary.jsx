import { Component } from "react";
import ServerError from "../pages/ServerError";

/**
 * Catches uncaught render errors anywhere in the app and renders the 500 page
 * instead of a blank screen. Deliberately dependency-free (class component).
 */
export default class ErrorBoundary extends Component {
  state = { error: null };

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    // Surface for debugging; never render user data here.
    console.error("[Sahaara] uncaught error:", error, info);
  }

  render() {
    if (this.state.error) {
      return <ServerError detail={this.state.error?.message} />;
    }
    return this.props.children;
  }
}
