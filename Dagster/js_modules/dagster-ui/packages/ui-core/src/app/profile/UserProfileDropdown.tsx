// dagster-master/js_modules/packages/app-oss/src/app/authentication/UserProfileDropdown.tsx

import * as React from 'react';
// Removed: import { useQuery } from '@apollo/client'; as it's not used in this version

// Import Icon and Popover from @dagster-io/ui (recommended for consistency)
import { Icon, Popover } from '@dagster-io/ui-components';
import styled from 'styled-components'; // For styling components

// Removed: import { CURRENT_USER_QUERY } from '../../graphql/types/CurrentUserQuery'; as it's not used

// Styled component for the profile button (visual styling)
const UserProfileButton = styled.button`
  background: none;
  border: none;
  color: white; /* Text and icon color for visibility on dark header */
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px; /* Space between icon and text */
  font-size: 14px;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.2s; /* Smooth hover effect */

  &:hover {
    background-color: rgba(255, 255, 255, 0.1); /* Subtle hover background */
  }
  &:focus {
    outline: none; /* Remove default focus outline */
    box-shadow: 0 0 0 2px rgba(0, 114, 195, 0.5); /* Custom focus outline */
  }
`;

// Styled div for the dropdown menu container
const DropdownMenuContainer = styled.div`
  background-color: #f9f9f9; /* Light background for the dropdown */
  min-width: 180px; /* Minimum width for the dropdown */
  box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2); /* Shadow for depth */
  border-radius: 4px; /* Rounded corners */
  overflow: hidden; /* Ensures content stays within rounded corners */
`;

// Styled link for individual menu items
const DropdownMenuItem = styled.a`
  color: #333; /* Dark text color */
  padding: 12px 16px;
  text-decoration: none; /* Remove underline from links */
  display: flex;
  align-items: center;
  gap: 10px; /* Space between icon and text in menu item */
  font-size: 14px;
  cursor: pointer; /* Show pointer cursor to indicate interactivity */

  &:hover {
    background-color: #f1f1f1; /* Light grey background on hover */
  }
  &:active {
    background-color: #e0e0e0; /* Slightly darker grey when clicked */
  }
`;

// The main UserProfileDropdown React component
export const UserProfileDropdown = () => {
  // GraphQL query related logic is commented out to avoid errors and simplify
  // const { data, loading, error } = useQuery(CURRENT_USER_QUERY);

  // State to control the visibility of the Popover (dropdown)
  const [isOpen, setIsOpen] = React.useState(false);

  // Loading/error/authentication checks are removed, so this component will always render.
  // if (loading || error) { return null; }
  // const username = data?.me?.username || 'Guest';
  // const isAuthenticated = data?.me?.isAuthenticated || false;
  // if (!isAuthenticated) { return null; }

  return (
    <Popover
        content={ /* Content that appears when the Popover is open (the dropdown menu) */
            <DropdownMenuContainer>
                {/* "My Profile" Button (currently not functional, just a link) */}
                <DropdownMenuItem href="#"> {/* The '#' makes it a non-navigating link */}
                    <Icon name="account_circle" /> {/* User icon from Dagster UI */}
                    My Profile
                </DropdownMenuItem>
                {/* "Logout" Button (functional) */}
                <DropdownMenuItem
                    href="/logout" /* Points to the logout URL handled by your backend */
                    onClick={(e) => {
                        e.preventDefault(); // Prevents the default anchor tag navigation
                        window.location.href = '/logout'; // Manually redirects the browser
                    }}
                >
                    <Icon name="logout" /> {/* Logout icon from Dagster UI */}
                    Logout
                </DropdownMenuItem>
            </DropdownMenuContainer>
        }
      position="bottom-right" /* Positions the dropdown relative to the button */
      isOpen={isOpen} /* Controls whether the dropdown is visible */
      onClose={() => setIsOpen(false)} /* Closes the dropdown when user clicks outside */
    >
      {/* The button itself, which triggers the Popover/dropdown */}
      <UserProfileButton onClick={() => setIsOpen(!isOpen)}>
        <Icon name="account_circle" color="white" /> {/* User icon, colored white */}
        {/* Username text is removed here as GraphQL query is commented out */}
      </UserProfileButton>
    </Popover>
  );
};