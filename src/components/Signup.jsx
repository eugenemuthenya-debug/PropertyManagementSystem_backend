import axios from "axios";
import React, { useState } from "react";

const Signup = () => {
  // we will need our states which detect change and re-render the page when these fields change or user types
  const [landlord_name, setLandlordname] = useState("");
  const [landlord_email, setLandlordemail] = useState("");
  const [landlord_password, setLandlordpassowrd] = useState("");
  const [phone_number, setphonenumber] = useState("");
  const [account_status, setAccountStatus] = useState("");

  // communication with the user
  const [loading, setLoading] = useState("");
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");
  const baseUrl = "https://propertymanagementsystem-backend-q270.onrender.com";

  const submit = async (e) => {
    e.preventDefault();

    setSuccess("");
    setError("");

    setLoading("Wait as you get registered...");

    try {
      // response
      const response = await axios.post(baseUrl + "/api/signup", {
        landlord_name,
        landlord_email,
        landlord_password,
        phone_number,
        account_status,
      });
      setLoading("");
      setSuccess(response.data.message);

      setLandlordemail("");
      setLandlordname("");
      setLandlordpassowrd("");
      setphonenumber("");
    } catch (error) {
      setLoading("");
      setSuccess("");
      if (error.response && error.response.data) {
        setError(error.response.data.error || "Signup failed");
      } else {
        setError("Network error. Please check your connection");
      }
    }
  };

  return (
    <form onSubmit={submit}>
      <h3>Welcome new user Signup?</h3>
      <h4>{loading}</h4>
      <h4>{error}</h4>
      <h5>{success}</h5>

      {/* landlord username */}
      <input
        type="text"
        required
        value={landlord_name}
        placeholder="Your name"
        onChange={(e) => setLandlordname(e.target.value)}
      />
      <br/>

      {/* password */}
      <input
        type="password"
        placeholder="Your new password"
        required
        value={landlord_password}
        onChange={(e) => setLandlordpassowrd(e.target.value)}
      />
      <br/>

      {/* phone number */}
      <input
        type="tel"
        placeholder="Your phone number"
        required
        value={phone_number}
        onChange={(e) => setphonenumber(e.target.value)}
      /><br/>

      {/* email*/}
      <input
        type="email"
        placeholder="Your Email"
        required
        value={landlord_email}
        onChange={(e) => setLandlordemail(e.target.value)}
      /><br/>

      <input
        type="text"
        placeholder="Account type in caps"
        value={account_status}
        required
        onChange={(e) => setAccountStatus(e.target.value)}
      /><br/>

      <button type="submit">Sign up</button>
    </form>
  );
};

export default Signup;
